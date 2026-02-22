"""Termii SMS service for sending SMS notifications."""

import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class TermiiService:
    """Service for sending SMS via Termii API."""

    BASE_URL = "https://api.termii.com/api"

    def __init__(self):
        """Initialize Termii service with API key."""
        self.api_key = settings.termii_api_key
        self.sender_id = settings.termii_sender_id or "Kenikool"

    async def send_sms(
        self,
        phone_number: str,
        message: str,
        message_type: str = "PLAIN",
    ) -> Optional[dict]:
        """
        Send SMS via Termii.

        Args:
            phone_number: Recipient phone number (E.164 format)
            message: SMS message content
            message_type: Message type (PLAIN or UNICODE)

        Returns:
            Response from Termii API or None if failed
        """
        try:
            payload = {
                "to": phone_number,
                "from": self.sender_id,
                "sms": message,
                "type": message_type,
                "api_key": self.api_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/sms/send",
                    json=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") == "ok":
                    logger.info(
                        f"SMS sent successfully to {phone_number}",
                        extra={"phone": phone_number, "message_id": result.get("message_id")},
                    )
                    return result
                else:
                    logger.error(
                        f"SMS send failed: {result.get('message')}",
                        extra={"phone": phone_number, "error": result},
                    )
                    return None

        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error sending SMS to {phone_number}: {str(e)}",
                extra={"phone": phone_number, "error": str(e)},
            )
            return None
        except Exception as e:
            logger.error(
                f"Error sending SMS to {phone_number}: {str(e)}",
                extra={"phone": phone_number, "error": str(e)},
            )
            return None

    async def send_bulk_sms(
        self,
        phone_numbers: list[str],
        message: str,
        message_type: str = "PLAIN",
    ) -> dict:
        """
        Send bulk SMS via Termii.

        Args:
            phone_numbers: List of recipient phone numbers
            message: SMS message content
            message_type: Message type (PLAIN or UNICODE)

        Returns:
            Dictionary with success and failed counts
        """
        results = {"success": 0, "failed": 0, "errors": []}

        for phone_number in phone_numbers:
            result = await self.send_sms(phone_number, message, message_type)
            if result:
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(phone_number)

        return results

    async def get_balance(self) -> Optional[float]:
        """
        Get account balance.

        Returns:
            Account balance or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/get-balance",
                    params={"api_key": self.api_key},
                    timeout=10.0,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("code") == "ok":
                    return float(result.get("balance", 0))
                else:
                    logger.error(f"Failed to get balance: {result.get('message')}")
                    return None

        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return None

    async def verify_phone(self, phone_number: str) -> Optional[dict]:
        """
        Verify phone number format.

        Args:
            phone_number: Phone number to verify

        Returns:
            Verification result or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/check/dnd",
                    params={
                        "phone_number": phone_number,
                        "api_key": self.api_key,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error verifying phone: {str(e)}")
            return None

    def send_sms_sync(
        self,
        phone_number: str,
        message: str,
        message_type: str = "PLAIN",
    ) -> Optional[dict]:
        """
        Send SMS via Termii (synchronous version).

        Args:
            phone_number: Recipient phone number (E.164 format)
            message: SMS message content
            message_type: Message type (PLAIN or UNICODE)

        Returns:
            Response from Termii API or None if failed
        """
        try:
            payload = {
                "to": phone_number,
                "from": self.sender_id,
                "sms": message,
                "type": message_type,
                "api_key": self.api_key,
            }

            response = httpx.post(
                f"{self.BASE_URL}/sms/send",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == "ok":
                logger.info(
                    f"SMS sent successfully to {phone_number}",
                    extra={"phone": phone_number, "message_id": result.get("message_id")},
                )
                return result
            else:
                logger.error(
                    f"SMS send failed: {result.get('message')}",
                    extra={"phone": phone_number, "error": result},
                )
                return None

        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error sending SMS to {phone_number}: {str(e)}",
                extra={"phone": phone_number, "error": str(e)},
            )
            return None
        except Exception as e:
            logger.error(
                f"Error sending SMS to {phone_number}: {str(e)}",
                extra={"phone": phone_number, "error": str(e)},
            )
            return None
