"""
Paystack payment service for processing recurring payments.
Handles payment processing, verification, and transaction management.
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class PaystackService:
    """Service for integrating with Paystack payment gateway"""

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        """Initialize Paystack service with API credentials"""
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
        self.webhook_secret = settings.PAYSTACK_WEBHOOK_SECRET
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self,
        email: str,
        amount: float,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a transaction on Paystack.

        This is typically used for one-time payments or to get an authorization code
        for recurring payments.

        Args:
            email: Customer email address
            amount: Amount in currency (will be converted to kobo)
            reference: Unique transaction reference
            metadata: Additional metadata to attach to transaction

        Returns:
            Response from Paystack with authorization_url and access_code

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/transaction/initialize"

        # Convert amount to kobo (Paystack uses smallest currency unit)
        amount_kobo = int(amount * 100)

        payload = {
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
        }

        if metadata:
            payload["metadata"] = metadata

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(
                    f"Initialized transaction {reference} for {email} "
                    f"with amount {amount}"
                )
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to initialize transaction: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for initialize_transaction: {str(e)}")
            raise Exception(f"Failed to initialize transaction: {str(e)}")

    async def charge_authorization(
        self,
        authorization_code: str,
        email: str,
        amount: float,
        reference: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Charge a stored authorization (recurring payment).

        This is used for charging a customer's stored card for subscription renewals.

        Args:
            authorization_code: Previously stored authorization code
            email: Customer email address
            amount: Amount in currency (will be converted to kobo)
            reference: Unique transaction reference
            metadata: Additional metadata to attach to transaction

        Returns:
            Response from Paystack with transaction details

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/transaction/charge_authorization"

        # Convert amount to kobo
        amount_kobo = int(amount * 100)

        payload = {
            "authorization_code": authorization_code,
            "email": email,
            "amount": amount_kobo,
            "reference": reference,
        }

        if metadata:
            payload["metadata"] = metadata

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(
                    f"Charged authorization {authorization_code} for {email} "
                    f"with amount {amount}"
                )
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to charge authorization: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for charge_authorization: {str(e)}")
            raise Exception(f"Failed to charge authorization: {str(e)}")

    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """
        Verify a transaction status.

        Args:
            reference: Transaction reference to verify

        Returns:
            Transaction details from Paystack

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/transaction/verify/{reference}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                transaction = result.get("data", {})
                logger.info(
                    f"Verified transaction {reference} with status "
                    f"{transaction.get('status')}"
                )
                return transaction
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to verify transaction: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for verify_transaction: {str(e)}")
            raise Exception(f"Failed to verify transaction: {str(e)}")

    async def get_customer(self, customer_code: str) -> Dict[str, Any]:
        """
        Get customer details from Paystack.

        Args:
            customer_code: Paystack customer code

        Returns:
            Customer details

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/customer/{customer_code}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Retrieved customer {customer_code}")
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to get customer: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for get_customer: {str(e)}")
            raise Exception(f"Failed to get customer: {str(e)}")

    async def create_customer(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a customer on Paystack.

        Args:
            email: Customer email
            first_name: Customer first name
            last_name: Customer last name
            phone: Customer phone number (optional)

        Returns:
            Created customer details

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/customer"

        payload = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }

        if phone:
            payload["phone"] = phone

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Created customer {email}")
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to create customer: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for create_customer: {str(e)}")
            raise Exception(f"Failed to create customer: {str(e)}")

    async def list_authorizations(self, customer_code: str) -> list:
        """
        List all authorizations for a customer.

        Args:
            customer_code: Paystack customer code

        Returns:
            List of authorizations

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/customer/{customer_code}/authorizations"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Retrieved authorizations for customer {customer_code}")
                return result.get("data", [])
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to list authorizations: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for list_authorizations: {str(e)}")
            raise Exception(f"Failed to list authorizations: {str(e)}")

    async def deactivate_authorization(
        self, authorization_code: str, email: str
    ) -> Dict[str, Any]:
        """
        Deactivate an authorization (stop recurring charges).

        Args:
            authorization_code: Authorization code to deactivate
            email: Customer email

        Returns:
            Response from Paystack

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/authorization/deactivate"

        payload = {
            "authorization_code": authorization_code,
            "email": email,
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Deactivated authorization {authorization_code}")
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to deactivate authorization: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for deactivate_authorization: {str(e)}")
            raise Exception(f"Failed to deactivate authorization: {str(e)}")

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Paystack.

        Args:
            payload: Raw request body
            signature: X-Paystack-Signature header value

        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib

        hash_object = hmac.new(
            self.webhook_secret.encode("utf-8"),
            payload,
            hashlib.sha512,
        )
        computed_signature = hash_object.hexdigest()

        is_valid = computed_signature == signature
        if not is_valid:
            logger.warning("Invalid webhook signature received")
        return is_valid

    async def get_transaction_timeline(self, reference: str) -> list:
        """
        Get timeline of events for a transaction.

        Args:
            reference: Transaction reference

        Returns:
            List of timeline events

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/transaction/timeline/{reference}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Retrieved timeline for transaction {reference}")
                return result.get("data", [])
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to get transaction timeline: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for get_transaction_timeline: {str(e)}")
            raise Exception(f"Failed to get transaction timeline: {str(e)}")

    async def create_plan(
        self,
        name: str,
        description: str,
        amount: float,
        interval: str,
        invoice_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Create a plan on Paystack for recurring billing.

        Args:
            name: Plan name
            description: Plan description
            amount: Amount in currency (will be converted to kobo)
            interval: Billing interval (monthly, quarterly, yearly)
            invoice_limit: Maximum number of invoices (optional)

        Returns:
            Created plan details

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/plan"

        # Convert amount to kobo
        amount_kobo = int(amount * 100)

        payload = {
            "name": name,
            "description": description,
            "amount": amount_kobo,
            "interval": interval,
        }

        if invoice_limit:
            payload["invoice_limit"] = invoice_limit

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Created plan {name}")
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to create plan: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for create_plan: {str(e)}")
            raise Exception(f"Failed to create plan: {str(e)}")

    async def create_subscription(
        self,
        customer_code: str,
        plan_code: str,
        authorization_code: str,
        start_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a subscription on Paystack.

        Args:
            customer_code: Paystack customer code
            plan_code: Paystack plan code
            authorization_code: Authorization code for charging
            start_date: Subscription start date (optional, ISO format)

        Returns:
            Created subscription details

        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/subscription"

        payload = {
            "customer": customer_code,
            "plan": plan_code,
            "authorization": authorization_code,
        }

        if start_date:
            payload["start_date"] = start_date

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            if result.get("status"):
                logger.info(f"Created subscription for customer {customer_code}")
                return result.get("data", {})
            else:
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Failed to create subscription: {error_msg}")
                raise Exception(f"Paystack error: {error_msg}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for create_subscription: {str(e)}")
            raise Exception(f"Failed to create subscription: {str(e)}")
