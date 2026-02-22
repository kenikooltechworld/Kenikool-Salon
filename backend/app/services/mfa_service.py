"""Multi-Factor Authentication (MFA) service."""

import logging
import secrets
from typing import Optional, Tuple, List
import pyotp
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class MFAService:
    """Service for managing Multi-Factor Authentication."""

    def __init__(self):
        """Initialize MFA service."""
        self.totp_issuer = "Salon SPA Gym"

    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()

    def get_totp_uri(self, secret: str, email: str, issuer: str = None) -> str:
        """Get the TOTP provisioning URI for QR code generation."""
        totp = pyotp.TOTP(secret)
        issuer_name = issuer or self.totp_issuer
        return totp.provisioning_uri(name=email, issuer_name=issuer_name)

    def generate_qr_code(self, uri: str) -> str:
        """Generate a QR code image as base64 string."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return ""

    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify a TOTP code."""
        try:
            totp = pyotp.TOTP(secret)
            # Allow for time drift (±1 time window)
            return totp.verify(code, valid_window=1)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {e}")
            return False

    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery."""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        return codes

    def hash_backup_code(self, code: str) -> str:
        """Hash a backup code for storage."""
        # In production, use bcrypt or similar
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()

    def verify_backup_code(self, code: str, backup_codes: List[str]) -> bool:
        """Verify a backup code is in the list."""
        return code in backup_codes

    def get_totp_code(self, secret: str) -> str:
        """Get the current TOTP code."""
        try:
            totp = pyotp.TOTP(secret)
            return totp.now()
        except Exception as e:
            logger.error(f"Error getting TOTP code: {e}")
            return ""

    def setup_totp(self, email: str) -> Tuple[str, str, List[str]]:
        """Set up TOTP for a user."""
        try:
            secret = self.generate_totp_secret()
            uri = self.get_totp_uri(secret, email)
            qr_code = self.generate_qr_code(uri)
            backup_codes = self.generate_backup_codes()

            logger.info(f"TOTP setup initiated for user: {email}")
            return secret, qr_code, backup_codes
        except Exception as e:
            logger.error(f"Error setting up TOTP: {e}")
            return "", "", []

    def setup_sms(self, phone: str) -> Optional[str]:
        """Set up SMS OTP for a user."""
        try:
            # Generate OTP code
            otp_code = secrets.randbelow(1000000)
            otp_code_str = str(otp_code).zfill(6)

            logger.info(f"SMS OTP setup initiated for phone: {phone}")
            # In production, send SMS via Twilio or similar
            return otp_code_str
        except Exception as e:
            logger.error(f"Error setting up SMS OTP: {e}")
            return None

    def verify_sms_code(self, provided_code: str, expected_code: str) -> bool:
        """Verify an SMS OTP code."""
        try:
            return provided_code == expected_code
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False

    def send_sms_otp(self, phone: str, code: str) -> bool:
        """Send SMS OTP to user."""
        try:
            # In production, use Twilio or similar SMS provider
            logger.info(f"SMS OTP sent to {phone}: {code}")
            return True
        except Exception as e:
            logger.error(f"Error sending SMS OTP: {e}")
            return False
