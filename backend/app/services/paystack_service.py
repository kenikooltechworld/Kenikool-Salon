"""Service for Paystack payment gateway integration."""

import os
import logging
import hmac
import hashlib
import json
from typing import Optional, Dict, Any
from decimal import Decimal
import requests
from bson import ObjectId

logger = logging.getLogger(__name__)

# Singleton instance
_paystack_service_instance: Optional['PaystackService'] = None
_initialized = False


class PaystackService:
    """Service for Paystack payment gateway integration."""

    # Paystack API endpoints
    BASE_URL = "https://api.paystack.co"
    INITIALIZE_URL = f"{BASE_URL}/transaction/initialize"
    VERIFY_URL = f"{BASE_URL}/transaction/verify"
    REFUND_URL = f"{BASE_URL}/refund"
    GET_TRANSACTION_URL = f"{BASE_URL}/transaction"

    def __init__(self):
        """Initialize Paystack service with API keys from environment."""
        global _initialized
        
        self.secret_key = os.getenv("PAYSTACK_LIVE_SECRET_KEY")
        self.public_key = os.getenv("PAYSTACK_LIVE_PUBLIC_KEY")
        self.webhook_secret = os.getenv("PAYSTACK_WEBHOOK_SECRET")

        # Only log warnings once
        if not _initialized:
            if not self.secret_key:
                logger.warning("PAYSTACK_LIVE_SECRET_KEY not configured")
            if not self.public_key:
                logger.warning("PAYSTACK_LIVE_PUBLIC_KEY not configured")
            _initialized = True

        logger.debug("Paystack service initialized")

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authorization."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def _log_api_call(
        self,
        method: str,
        endpoint: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log API calls for audit trail."""
        log_entry = {
            "method": method,
            "endpoint": endpoint,
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }

        if request_data:
            # Don't log sensitive data
            safe_data = request_data.copy()
            if "card" in safe_data:
                safe_data["card"] = "***REDACTED***"
            log_entry["request"] = safe_data

        if response_data:
            log_entry["response"] = response_data

        if error:
            log_entry["error"] = error
            logger.error(f"Paystack API error: {json.dumps(log_entry)}")
        else:
            logger.info(f"Paystack API call: {json.dumps(log_entry)}")

    def initialize_transaction(
        self,
        amount: Decimal,
        email: str,
        callback_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a Paystack transaction.

        Args:
            amount: Transaction amount in naira
            email: Customer email address
            callback_url: URL to redirect to after payment
            metadata: Optional metadata dictionary

        Returns:
            Dictionary with transaction data including authorization_url

        Raises:
            ValueError: If amount is invalid
            requests.RequestException: If API call fails
        """
        if not amount or amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if not email:
            raise ValueError("Email is required")

        # Convert amount to kobo (Paystack uses smallest currency unit)
        amount_kobo = int(amount * 100)

        request_data = {
            "amount": amount_kobo,
            "email": email,
        }

        if callback_url:
            request_data["callback_url"] = callback_url

        if metadata:
            request_data["metadata"] = metadata

        try:
            logger.info(f"Initializing Paystack transaction for {email}, amount: {amount}")

            response = requests.post(
                self.INITIALIZE_URL,
                headers=self._get_headers(),
                json=request_data,
                timeout=10,
            )

            response.raise_for_status()
            response_data = response.json()

            self._log_api_call(
                "POST",
                "transaction/initialize",
                request_data=request_data,
                response_data=response_data,
            )

            if not response_data.get("status"):
                error_msg = response_data.get("message", "Unknown error")
                logger.error(f"Paystack initialization failed: {error_msg}")
                raise ValueError(f"Paystack error: {error_msg}")

            return response_data.get("data", {})

        except requests.exceptions.RequestException as e:
            error_msg = f"Paystack API request failed: {str(e)}"
            logger.error(error_msg)
            self._log_api_call(
                "POST",
                "transaction/initialize",
                request_data=request_data,
                error=error_msg,
            )
            raise

    def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """
        Verify a Paystack transaction.

        Args:
            reference: Transaction reference from Paystack

        Returns:
            Dictionary with transaction verification data

        Raises:
            ValueError: If reference is invalid
            requests.RequestException: If API call fails
        """
        if not reference:
            raise ValueError("Reference is required")

        try:
            logger.info(f"Verifying Paystack transaction: {reference}")

            url = f"{self.VERIFY_URL}/{reference}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10,
            )

            response.raise_for_status()
            response_data = response.json()

            self._log_api_call(
                "GET",
                f"transaction/verify/{reference}",
                response_data=response_data,
            )

            if not response_data.get("status"):
                error_msg = response_data.get("message", "Unknown error")
                logger.error(f"Paystack verification failed: {error_msg}")
                raise ValueError(f"Paystack error: {error_msg}")

            return response_data.get("data", {})

        except requests.exceptions.RequestException as e:
            error_msg = f"Paystack API request failed: {str(e)}"
            logger.error(error_msg)
            self._log_api_call(
                "GET",
                f"transaction/verify/{reference}",
                error=error_msg,
            )
            raise

    def get_transaction(self, transaction_id: int) -> Dict[str, Any]:
        """
        Get transaction details by ID.

        Args:
            transaction_id: Paystack transaction ID

        Returns:
            Dictionary with transaction data

        Raises:
            ValueError: If transaction_id is invalid
            requests.RequestException: If API call fails
        """
        if not transaction_id or transaction_id <= 0:
            raise ValueError("Transaction ID must be a positive integer")

        try:
            logger.info(f"Getting Paystack transaction: {transaction_id}")

            url = f"{self.GET_TRANSACTION_URL}/{transaction_id}"
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10,
            )

            response.raise_for_status()
            response_data = response.json()

            self._log_api_call(
                "GET",
                f"transaction/{transaction_id}",
                response_data=response_data,
            )

            if not response_data.get("status"):
                error_msg = response_data.get("message", "Unknown error")
                logger.error(f"Paystack get transaction failed: {error_msg}")
                raise ValueError(f"Paystack error: {error_msg}")

            return response_data.get("data", {})

        except requests.exceptions.RequestException as e:
            error_msg = f"Paystack API request failed: {str(e)}"
            logger.error(error_msg)
            self._log_api_call(
                "GET",
                f"transaction/{transaction_id}",
                error=error_msg,
            )
            raise

    def refund_transaction(
        self,
        reference: str,
        amount: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """
        Refund a Paystack transaction.

        Args:
            reference: Transaction reference
            amount: Optional refund amount in kobo (if not provided, full refund)

        Returns:
            Dictionary with refund data

        Raises:
            ValueError: If reference is invalid
            requests.RequestException: If API call fails
        """
        if not reference:
            raise ValueError("Reference is required")

        request_data = {
            "transaction": reference,
        }

        if amount is not None:
            if amount <= 0:
                raise ValueError("Refund amount must be greater than 0")
            # Convert to kobo
            request_data["amount"] = int(amount * 100)

        try:
            logger.info(f"Refunding Paystack transaction: {reference}, amount: {amount}")

            response = requests.post(
                self.REFUND_URL,
                headers=self._get_headers(),
                json=request_data,
                timeout=10,
            )

            response.raise_for_status()
            response_data = response.json()

            self._log_api_call(
                "POST",
                "refund",
                request_data=request_data,
                response_data=response_data,
            )

            if not response_data.get("status"):
                error_msg = response_data.get("message", "Unknown error")
                logger.error(f"Paystack refund failed: {error_msg}")
                raise ValueError(f"Paystack error: {error_msg}")

            return response_data.get("data", {})

        except requests.exceptions.RequestException as e:
            error_msg = f"Paystack API request failed: {str(e)}"
            logger.error(error_msg)
            self._log_api_call(
                "POST",
                "refund",
                request_data=request_data,
                error=error_msg,
            )
            raise

    def verify_webhook_signature(self, request_body: str, signature: str) -> bool:
        """
        Verify Paystack webhook signature.

        Args:
            request_body: Raw request body as string
            signature: Signature from X-Paystack-Signature header

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False

        try:
            # Compute HMAC-SHA512 hash
            computed_hash = hmac.new(
                self.webhook_secret.encode(),
                request_body.encode(),
                hashlib.sha512,
            ).hexdigest()

            # Compare with provided signature
            is_valid = computed_hash == signature
            if not is_valid:
                logger.warning(f"Invalid webhook signature: {signature}")
            return is_valid

        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

    def extract_webhook_data(self, webhook_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant data from Paystack webhook.

        Args:
            webhook_body: Webhook request body

        Returns:
            Dictionary with extracted data

        Raises:
            ValueError: If webhook data is invalid
        """
        event = webhook_body.get("event")
        data = webhook_body.get("data", {})

        if not event:
            raise ValueError("Webhook event not found")

        if event == "charge.success":
            return {
                "event": "charge.success",
                "status": "success",
                "reference": data.get("reference"),
                "amount": data.get("amount"),
                "customer_email": data.get("customer", {}).get("email"),
                "transaction_id": data.get("id"),
                "authorization": data.get("authorization", {}),
                "paid_at": data.get("paid_at"),
            }

        elif event == "charge.failed":
            return {
                "event": "charge.failed",
                "status": "failed",
                "reference": data.get("reference"),
                "amount": data.get("amount"),
                "customer_email": data.get("customer", {}).get("email"),
                "transaction_id": data.get("id"),
                "failure_reason": data.get("gateway_response"),
                "paid_at": data.get("paid_at"),
            }

        else:
            logger.info(f"Unhandled webhook event: {event}")
            return {
                "event": event,
                "data": data,
            }
