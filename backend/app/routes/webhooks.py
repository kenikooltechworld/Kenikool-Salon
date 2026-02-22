"""Webhook routes for handling third-party integrations."""

import logging
import json
from typing import Dict, Any
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, status
from bson import ObjectId
from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.refund import Refund
from app.models.appointment import Appointment
from app.services.paystack_service import PaystackService
from app.services.payment_service import PaymentService
from app.services.invoice_service import InvoiceService
from app.services.refund_service import RefundService
from app.services.audit_service import AuditService
from app.services.appointment_service import AppointmentService
from app.tasks import queue_notification
from app.context import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Lazy initialization to avoid repeated instantiation during reload
_paystack_service = None
_payment_service = None
_refund_service = None
_audit_service = None


def get_paystack_service():
    """Get or create PaystackService instance."""
    global _paystack_service
    if _paystack_service is None:
        _paystack_service = PaystackService()
    return _paystack_service


def get_payment_service():
    """Get or create PaymentService instance."""
    global _payment_service
    if _payment_service is None:
        _payment_service = PaymentService()
    return _payment_service


def get_refund_service():
    """Get or create RefundService instance."""
    global _refund_service
    if _refund_service is None:
        _refund_service = RefundService()
    return _refund_service


def get_audit_service():
    """Get or create AuditService instance."""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service


@router.post("/paystack")
async def handle_paystack_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle Paystack webhook events.
    
    Verifies webhook signature, processes payment events, and updates payment status.
    Supports charge.success and charge.failed events.
    """
    try:
        # Get request body as raw bytes
        body = await request.body()
        body_str = body.decode("utf-8")
        
        # Get signature from header
        signature = request.headers.get("X-Paystack-Signature")
        if not signature:
            logger.warning("Webhook received without signature header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Paystack-Signature header"
            )
        
        # Verify webhook signature
        if not get_paystack_service().verify_webhook_signature(body_str, signature):
            logger.warning(f"Webhook signature verification failed for signature: {signature}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        # Parse webhook body
        webhook_data = json.loads(body_str)
        logger.info(f"Valid webhook received: {webhook_data.get('event')}")
        
        # Extract webhook data
        extracted_data = get_paystack_service().extract_webhook_data(webhook_data)
        
        # Get payment by reference (without tenant context - webhooks come from Paystack servers)
        reference = extracted_data.get("reference")
        # Query payment directly from database without tenant context
        from app.models.payment import Payment as PaymentModel
        payment = PaymentModel.objects(reference=reference).first()
        
        if not payment:
            logger.warning(f"Payment not found for reference: {reference}")
            # Log webhook event even if payment not found
            await get_audit_service().log_event(
                event_type="webhook",
                resource="/webhooks/paystack",
                status_code=404,
                request_body=webhook_data,
                tags=["webhook", "paystack", "payment_not_found"],
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment not found for reference: {reference}"
            )
        
        # Get tenant context from payment
        tenant_id = str(payment.tenant_id)
        
        # Handle different webhook events
        event = webhook_data.get("event")
        
        if event == "charge.success":
            await _handle_charge_success(payment, extracted_data, tenant_id, webhook_data)
        elif event == "charge.failed":
            await _handle_charge_failed(payment, extracted_data, tenant_id, webhook_data)
        elif event == "refund.success":
            await _handle_refund_success(extracted_data, tenant_id, webhook_data)
        else:
            logger.info(f"Unhandled webhook event: {event}")
            await get_audit_service().log_event(
                event_type="webhook",
                resource="/webhooks/paystack",
                status_code=200,
                request_body=webhook_data,
                tags=["webhook", "paystack", "unhandled_event"],
            )
        
        return {"success": True, "message": "Webhook processed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Paystack webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


async def _handle_charge_success(
    payment: Payment,
    extracted_data: Dict[str, Any],
    tenant_id: str,
    webhook_data: Dict[str, Any],
) -> None:
    """Handle successful charge event."""
    try:
        logger.info(f"Processing charge.success for payment {payment.id}")
        logger.info(f"Payment metadata: {payment.metadata}")
        logger.info(f"Payment type: {payment.metadata.get('payment_type')}")
        
        # Update payment status
        payment.status = "success"
        payment.metadata.update({
            "paystack_transaction_id": extracted_data.get("transaction_id"),
            "paystack_authorization": extracted_data.get("authorization"),
            "webhook_processed_at": str(extracted_data.get("paid_at")),
        })
        payment.save()
        logger.info(f"Payment {payment.id} marked as success")
        
        # Handle booking payment (create appointment if booking data exists)
        if payment.metadata.get("payment_type") == "booking":
            logger.info(f"Booking payment detected for {payment.id}, creating booking...")
            await _create_booking_from_payment(payment, tenant_id, webhook_data)
        elif payment.metadata.get("payment_type") == "pos":
            logger.info(f"POS payment detected for {payment.id}, creating transaction...")
            await _create_transaction_from_payment(payment, tenant_id, webhook_data)
        else:
            logger.info(f"Non-booking/POS payment {payment.id}, skipping creation")
        
        # Mark invoice as paid and update appointment
        invoice = Invoice.objects(
            tenant_id=ObjectId(tenant_id),
            id=payment.invoice_id
        ).first()
        
        if invoice:
            InvoiceService.mark_invoice_paid(
                tenant_id=ObjectId(tenant_id),
                invoice_id=payment.invoice_id
            )
            logger.info(f"Invoice {invoice.id} marked as paid")
            
            # Update appointment if linked to invoice
            if invoice.appointment_id:
                from app.models.appointment import Appointment
                appointment = Appointment.objects(
                    tenant_id=ObjectId(tenant_id),
                    id=invoice.appointment_id
                ).first()
                if appointment:
                    appointment.payment_id = payment.id
                    appointment.save()
                    logger.info(f"Appointment {appointment.id} updated with payment_id {payment.id}")
        else:
            logger.warning(f"Invoice {payment.invoice_id} not found for payment {payment.id}")
        
        # Log audit event
        await get_audit_service().log_event(
            event_type="webhook",
            resource="/webhooks/paystack",
            tenant_id=tenant_id,
            status_code=200,
            request_body=webhook_data,
            tags=["webhook", "paystack", "charge_success", "payment_success"],
        )
        
        # Queue notification for customer
        queue_notification(
            tenant_id=tenant_id,
            notification_type="payment_success",
            recipient_id=str(payment.customer_id) if payment.customer_id else None,
            data={
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "reference": payment.reference,
            }
        )
        logger.info(f"Notification queued for payment {payment.id}")
        
    except Exception as e:
        logger.error(f"Error handling charge.success: {e}", exc_info=True)
        raise


async def _send_booking_confirmation_email(
    tenant_id: ObjectId,
    appointment_id: ObjectId,
    customer_email: str,
    customer_name: str,
) -> None:
    """Send booking confirmation email to customer."""
    try:
        from app.models.tenant import Tenant
        from app.models.staff import Staff
        from app.models.service import Service
        from app.models.user import User
        from app.tasks import send_email
        
        # Get appointment details
        appointment = Appointment.objects(
            tenant_id=tenant_id,
            id=appointment_id
        ).first()
        
        if not appointment:
            logger.warning(f"Appointment {appointment_id} not found for email")
            return
        
        # Get tenant, service, and staff details
        tenant = Tenant.objects(id=tenant_id).first()
        service = Service.objects(tenant_id=tenant_id, id=appointment.service_id).first()
        staff = Staff.objects(tenant_id=tenant_id, id=appointment.staff_id).first()
        
        if not tenant or not service or not staff:
            logger.warning(f"Missing tenant, service, or staff for appointment {appointment_id}")
            return
        
        # Get staff user details
        staff_user = User.objects(id=staff.user_id).first()
        staff_name = f"{staff_user.first_name} {staff_user.last_name}".strip() if staff_user else "Staff"
        
        # Format booking details
        booking_date_str = appointment.start_time.strftime("%B %d, %Y")
        booking_time_str = appointment.start_time.strftime("%I:%M %p")
        price_str = f"₦{float(service.price):,.2f}" if service.price else "N/A"
        
        # Calculate duration
        duration_minutes = int((appointment.end_time - appointment.start_time).total_seconds() / 60)
        
        # Queue email task
        context = {
            "customer_name": customer_name,
            "salon_name": tenant.name,
            "service_name": service.name,
            "staff_name": staff_name,
            "booking_date": booking_date_str,
            "booking_time": booking_time_str,
            "duration_minutes": duration_minutes,
            "price": price_str,
            "booking_id": str(appointment.id),
            "salon_address": tenant.address or "Address not provided",
            "salon_phone": tenant.phone or "Phone not provided",
            "salon_email": tenant.email or "Email not provided",
            "reschedule_link": f"https://{tenant.subdomain}.kenikool.com/reschedule/{appointment.id}",
            "cancellation_link": f"https://{tenant.subdomain}.kenikool.com/cancel/{appointment.id}",
            "current_year": datetime.utcnow().year,
        }
        
        send_email.delay(
            to=customer_email,
            subject=f"Booking Confirmation - {service.name} at {tenant.name}",
            template="booking_confirmation",
            context=context,
        )
        
        logger.info(f"Booking confirmation email queued for {customer_email}")
        
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {e}", exc_info=True)


async def _create_booking_from_payment(
    payment: Payment,
    tenant_id: str,
    webhook_data: Dict[str, Any],
) -> None:
    """Create a booking appointment from a successful booking payment."""
    try:
        logger.info(f"Creating booking from payment {payment.id}")
        logger.info(f"Payment metadata keys: {list(payment.metadata.keys())}")
        
        # Extract booking data from payment metadata
        booking_data = payment.metadata.get("booking_data", {})
        if not booking_data:
            logger.warning(f"No booking_data found in payment {payment.id} metadata")
            logger.warning(f"Available metadata: {payment.metadata}")
            return
        
        logger.info(f"Booking data found: {booking_data}")
        
        # Extract required fields
        customer_id = booking_data.get("customerId")
        service_id = booking_data.get("serviceId")
        staff_id = booking_data.get("staffId")
        start_time_str = booking_data.get("startTime")
        end_time_str = booking_data.get("endTime")
        customer_email = booking_data.get("customerEmail")
        customer_name = booking_data.get("customerName")
        
        logger.info(f"Extracted fields: customer_id={customer_id}, service_id={service_id}, staff_id={staff_id}")
        
        # Validate required fields
        if not all([customer_id, service_id, staff_id, start_time_str, end_time_str]):
            logger.warning(
                f"Missing required booking fields in payment {payment.id}. "
                f"Got: customer_id={customer_id}, service_id={service_id}, "
                f"staff_id={staff_id}, start_time={start_time_str}, end_time={end_time_str}"
            )
            return
        
        # Parse datetime strings
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            logger.info(f"Parsed times: start={start_time}, end={end_time}")
        except (ValueError, AttributeError) as e:
            logger.error(f"Error parsing datetime for payment {payment.id}: {e}")
            return
        
        # Check if appointment already exists (idempotency)
        existing_appointment = Appointment.objects(
            tenant_id=ObjectId(tenant_id),
            customer_id=ObjectId(customer_id),
            staff_id=ObjectId(staff_id),
            service_id=ObjectId(service_id),
            start_time=start_time,
            end_time=end_time,
        ).first()
        
        if existing_appointment:
            logger.info(
                f"Appointment already exists for payment {payment.id}. "
                f"Appointment ID: {existing_appointment.id}"
            )
            payment.metadata["appointment_id"] = str(existing_appointment.id)
            payment.save()
            logger.info(f"Updated payment metadata with existing appointment_id: {existing_appointment.id}")
            # Send confirmation email for existing appointment
            try:
                await _send_booking_confirmation_email(
                    tenant_id=ObjectId(tenant_id),
                    appointment_id=existing_appointment.id,
                    customer_email=customer_email,
                    customer_name=customer_name,
                )
            except Exception as e:
                logger.error(f"Error sending confirmation email: {e}")
            return
        
        # Create appointment
        logger.info(f"Creating new appointment for payment {payment.id}")
        appointment = AppointmentService.create_appointment(
            tenant_id=ObjectId(tenant_id),
            customer_id=ObjectId(customer_id),
            staff_id=ObjectId(staff_id),
            service_id=ObjectId(service_id),
            start_time=start_time,
            end_time=end_time,
            payment_option="now",
            payment_id=payment.id,
        )
        
        logger.info(f"Appointment created: {appointment.id} from payment {payment.id}")
        
        # Store appointment ID in payment metadata
        payment.metadata["appointment_id"] = str(appointment.id)
        payment.save()
        logger.info(f"Updated payment metadata with appointment_id: {appointment.id}")
        
        # Send confirmation email
        try:
            await _send_booking_confirmation_email(
                tenant_id=ObjectId(tenant_id),
                appointment_id=appointment.id,
                customer_email=customer_email,
                customer_name=customer_name,
            )
        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
        
        # Log audit event
        await get_audit_service().log_event(
            event_type="webhook",
            resource="/webhooks/paystack",
            tenant_id=tenant_id,
            status_code=200,
            request_body=webhook_data,
            tags=["webhook", "paystack", "booking_created", "appointment_created"],
        )
        
    except Exception as e:
        logger.error(f"Error creating booking from payment {payment.id}: {e}", exc_info=True)
        # Don't raise - we want webhook to succeed even if booking creation fails
        # The frontend can retry or the user can contact support


async def _create_transaction_from_payment(
    payment: Payment,
    tenant_id: str,
    webhook_data: Dict[str, Any],
) -> None:
    """Create a POS transaction from a successful payment."""
    try:
        logger.info(f"Creating transaction from payment {payment.id}")
        
        # Extract transaction data from payment metadata
        metadata = payment.metadata.get("metadata", {})
        customer_id = metadata.get("customer_id")
        staff_id = metadata.get("staff_id")
        
        if not customer_id or not staff_id:
            logger.warning(f"Missing customer_id or staff_id in payment {payment.id} metadata")
            return
        
        # Import transaction service
        from app.services.transaction_service import TransactionService
        
        # Create transaction with payment status as completed
        transaction = TransactionService.create_transaction(
            tenant_id=ObjectId(tenant_id),
            customer_id=ObjectId(customer_id),
            staff_id=ObjectId(staff_id),
            items_data=metadata.get("items", []),
            payment_method=metadata.get("payment_method", "card"),
            transaction_type="service",
            discount_amount=Decimal(str(metadata.get("discount_amount", 0))),
        )
        
        # Update transaction payment status to completed
        transaction.payment_status = "completed"
        transaction.paystack_reference = payment.reference
        transaction.save()
        
        logger.info(f"Transaction {transaction.id} created from payment {payment.id}")
        
    except Exception as e:
        logger.error(f"Error creating transaction from payment {payment.id}: {e}", exc_info=True)
        # Don't raise - we want webhook to succeed even if transaction creation fails


async def _handle_charge_failed(
    payment: Payment,
    extracted_data: Dict[str, Any],
    tenant_id: str,
    webhook_data: Dict[str, Any],
) -> None:
    """Handle failed charge event."""
    try:
        logger.info(f"Processing charge.failed for payment {payment.id}")
        
        # Update payment status
        payment.status = "failed"
        failure_reason = extracted_data.get("failure_reason", "Unknown reason")
        payment.metadata.update({
            "failure_reason": failure_reason,
            "paystack_transaction_id": extracted_data.get("transaction_id"),
            "webhook_processed_at": str(extracted_data.get("paid_at")),
        })
        payment.save()
        logger.info(f"Payment {payment.id} marked as failed. Reason: {failure_reason}")
        
        # Log audit event
        await get_audit_service().log_event(
            event_type="webhook",
            resource="/webhooks/paystack",
            tenant_id=tenant_id,
            status_code=200,
            request_body=webhook_data,
            tags=["webhook", "paystack", "charge_failed", "payment_failed"],
        )
        
        # Queue notification for customer
        queue_notification(
            tenant_id=tenant_id,
            notification_type="payment_failed",
            recipient_id=str(payment.customer_id),
            data={
                "payment_id": str(payment.id),
                "amount": str(payment.amount),
                "reference": payment.reference,
                "reason": failure_reason,
            }
        )
        logger.info(f"Notification queued for customer {payment.customer_id}")
        
    except Exception as e:
        logger.error(f"Error handling charge.failed: {e}", exc_info=True)
        raise


async def _handle_refund_success(
    extracted_data: Dict[str, Any],
    tenant_id: str,
    webhook_data: Dict[str, Any],
) -> None:
    """Handle successful refund event."""
    try:
        logger.info(f"Processing refund.success event")
        
        # Get refund reference from webhook data
        refund_reference = webhook_data.get("data", {}).get("reference")
        if not refund_reference:
            logger.warning("Refund reference not found in webhook data")
            return
        
        # Find refund by reference
        refund = Refund.objects(
            tenant_id=ObjectId(tenant_id),
            reference=refund_reference
        ).first()
        
        if not refund:
            logger.warning(f"Refund not found for reference: {refund_reference}")
            await get_audit_service().log_event(
                event_type="webhook",
                resource="/webhooks/paystack",
                tenant_id=tenant_id,
                status_code=404,
                request_body=webhook_data,
                tags=["webhook", "paystack", "refund_not_found"],
            )
            return
        
        # Update refund status to success
        refund.status = "success"
        refund.metadata.update({
            "paystack_refund_id": extracted_data.get("transaction_id"),
            "webhook_processed_at": str(extracted_data.get("paid_at")),
        })
        refund.save()
        logger.info(f"Refund {refund.id} marked as success")
        
        # Update Payment record to reflect refund
        payment = Payment.objects(
            tenant_id=ObjectId(tenant_id),
            id=refund.payment_id
        ).first()
        
        if payment:
            payment.metadata.update({
                "refund_id": str(refund.id),
                "refund_amount": str(refund.amount),
                "refund_status": "success",
            })
            payment.save()
            logger.info(f"Payment {payment.id} updated with refund information")
        else:
            logger.warning(f"Payment {refund.payment_id} not found for refund {refund.id}")
        
        # Log audit event
        await get_audit_service().log_event(
            event_type="webhook",
            resource="/webhooks/paystack",
            tenant_id=tenant_id,
            status_code=200,
            request_body=webhook_data,
            tags=["webhook", "paystack", "refund_success"],
        )
        
        # Queue notification for customer
        if payment:
            queue_notification(
                tenant_id=tenant_id,
                notification_type="refund_success",
                recipient_id=str(payment.customer_id),
                data={
                    "refund_id": str(refund.id),
                    "payment_id": str(payment.id),
                    "amount": str(refund.amount),
                    "reference": refund.reference,
                }
            )
            logger.info(f"Notification queued for customer {payment.customer_id}")
        
    except Exception as e:
        logger.error(f"Error handling refund.success: {e}", exc_info=True)
        raise
