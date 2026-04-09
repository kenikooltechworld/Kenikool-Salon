"""Customer deletion service with cascading deletion of all related data."""

import logging
from typing import Dict, Any
from bson import ObjectId
from app.models.customer import Customer
from app.models.appointment import Appointment
from app.models.appointment_history import AppointmentHistory
from app.models.customer_preference import CustomerPreference
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.membership import Membership, MembershipTransaction
from app.models.receipt import Receipt
from app.models.transaction import Transaction
from app.models.cart import Cart
from app.models.time_slot import TimeSlot
from app.models.waiting_room import QueueEntry, QueueHistory
from app.models.public_booking import PublicBooking
from app.models.customer_recommendation import CustomerPreference as RecommendationPreference, BookingRecommendation
from app.models.group_booking import GroupBooking
from app.models.notification import Notification, NotificationPreference
from app.models.refund import Refund

logger = logging.getLogger(__name__)


class CustomerDeletionService:
    """Service for handling customer deletion with cascading deletes."""

    @staticmethod
    def delete_customer_and_related_data(
        tenant_id: ObjectId,
        customer_id: ObjectId
    ) -> Dict[str, Any]:
        """
        Delete a customer and all their related data across all collections.
        
        Args:
            tenant_id: The tenant ID
            customer_id: The customer ID to delete
            
        Returns:
            Dictionary with deletion statistics
            
        Raises:
            ValueError: If customer not found
        """
        # Verify customer exists
        customer = Customer.objects(id=customer_id, tenant_id=tenant_id).first()
        if not customer:
            raise ValueError("Customer not found")
        
        deletion_stats = {
            "customer_id": str(customer_id),
            "customer_name": f"{customer.first_name} {customer.last_name}",
            "deleted_records": {}
        }
        
        try:
            # Delete appointments
            appointments_deleted = Appointment.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["appointments"] = appointments_deleted
            logger.info(f"Deleted {appointments_deleted} appointments for customer {customer_id}")
            
            # Delete appointment history
            history_deleted = AppointmentHistory.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["appointment_history"] = history_deleted
            logger.info(f"Deleted {history_deleted} appointment history records for customer {customer_id}")
            
            # Delete customer preferences
            preferences_deleted = CustomerPreference.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["customer_preferences"] = preferences_deleted
            logger.info(f"Deleted {preferences_deleted} customer preferences for customer {customer_id}")
            
            # Delete invoices
            invoices_deleted = Invoice.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["invoices"] = invoices_deleted
            logger.info(f"Deleted {invoices_deleted} invoices for customer {customer_id}")
            
            # Delete payments
            payments_deleted = Payment.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["payments"] = payments_deleted
            logger.info(f"Deleted {payments_deleted} payments for customer {customer_id}")
            
            # Delete memberships
            memberships_deleted = Membership.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["memberships"] = memberships_deleted
            logger.info(f"Deleted {memberships_deleted} memberships for customer {customer_id}")
            
            # Delete membership transactions
            membership_transactions_deleted = MembershipTransaction.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["membership_transactions"] = membership_transactions_deleted
            logger.info(f"Deleted {membership_transactions_deleted} membership transactions for customer {customer_id}")
            
            # Delete receipts
            receipts_deleted = Receipt.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["receipts"] = receipts_deleted
            logger.info(f"Deleted {receipts_deleted} receipts for customer {customer_id}")
            
            # Delete transactions
            transactions_deleted = Transaction.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["transactions"] = transactions_deleted
            logger.info(f"Deleted {transactions_deleted} transactions for customer {customer_id}")
            
            # Delete carts
            carts_deleted = Cart.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["carts"] = carts_deleted
            logger.info(f"Deleted {carts_deleted} carts for customer {customer_id}")
            
            # Delete time slots
            time_slots_deleted = TimeSlot.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["time_slots"] = time_slots_deleted
            logger.info(f"Deleted {time_slots_deleted} time slots for customer {customer_id}")
            
            # Delete waiting room entries
            waiting_room_deleted = QueueEntry.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["waiting_room_entries"] = waiting_room_deleted
            logger.info(f"Deleted {waiting_room_deleted} waiting room entries for customer {customer_id}")
            
            # Delete waiting room history
            waiting_room_history_deleted = QueueHistory.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["waiting_room_history"] = waiting_room_history_deleted
            logger.info(f"Deleted {waiting_room_history_deleted} waiting room history records for customer {customer_id}")
            
            # Delete public bookings
            public_bookings_deleted = PublicBooking.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["public_bookings"] = public_bookings_deleted
            logger.info(f"Deleted {public_bookings_deleted} public bookings for customer {customer_id}")
            
            # Delete customer recommendation preferences
            recommendation_prefs_deleted = RecommendationPreference.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["recommendation_preferences"] = recommendation_prefs_deleted
            logger.info(f"Deleted {recommendation_prefs_deleted} recommendation preferences for customer {customer_id}")
            
            # Delete customer recommendations
            recommendations_deleted = BookingRecommendation.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["recommendations"] = recommendations_deleted
            logger.info(f"Deleted {recommendations_deleted} recommendations for customer {customer_id}")
            
            # Delete group bookings where customer is the organizer
            group_bookings_deleted = GroupBooking.objects(
                tenant_id=tenant_id,
                organizer_customer_id=customer_id
            ).delete()
            deletion_stats["deleted_records"]["group_bookings"] = group_bookings_deleted
            logger.info(f"Deleted {group_bookings_deleted} group bookings for customer {customer_id}")
            
            # Delete notifications for this customer
            notifications_deleted = Notification.objects(
                tenant_id=tenant_id,
                recipient_id=str(customer_id),
                recipient_type="customer"
            ).delete()
            deletion_stats["deleted_records"]["notifications"] = notifications_deleted
            logger.info(f"Deleted {notifications_deleted} notifications for customer {customer_id}")
            
            # Delete notification preferences for this customer
            notification_prefs_deleted = NotificationPreference.objects(
                tenant_id=tenant_id,
                customer_id=str(customer_id),
                recipient_type="customer"
            ).delete()
            deletion_stats["deleted_records"]["notification_preferences"] = notification_prefs_deleted
            logger.info(f"Deleted {notification_prefs_deleted} notification preferences for customer {customer_id}")
            
            # Delete refunds related to customer's payments
            # First get all payment IDs for this customer
            customer_payments = Payment.objects(
                tenant_id=tenant_id,
                customer_id=customer_id
            ).only('id')
            payment_ids = [p.id for p in customer_payments]
            
            # Delete refunds for those payments
            refunds_deleted = 0
            if payment_ids:
                refunds_deleted = Refund.objects(
                    tenant_id=tenant_id,
                    payment_id__in=payment_ids
                ).delete()
            deletion_stats["deleted_records"]["refunds"] = refunds_deleted
            logger.info(f"Deleted {refunds_deleted} refunds for customer {customer_id}")
            
            # Finally, delete the customer
            customer.delete()
            deletion_stats["customer_deleted"] = True
            logger.info(f"Successfully deleted customer {customer_id} and all related data")
            
            # Verify customer is actually deleted
            verify_customer = Customer.objects(id=customer_id, tenant_id=tenant_id).first()
            if verify_customer:
                logger.error(f"Customer {customer_id} still exists after deletion!")
                raise Exception("Customer deletion verification failed")
            
            # Calculate total records deleted
            total_deleted = sum(deletion_stats["deleted_records"].values())
            deletion_stats["total_related_records_deleted"] = total_deleted
            
            return deletion_stats
            
        except Exception as e:
            logger.error(f"Error during customer deletion: {str(e)}", exc_info=True)
            raise
