"""Registration service for salon owner registration flow."""

import re
import secrets
import string
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from app.models.temp_registration import TempRegistration
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.session import Session
from app.config import Settings

logger = logging.getLogger(__name__)


class RegistrationService:
    """Service for handling salon owner registration."""

    def __init__(self, settings: Settings):
        """Initialize registration service."""
        self.settings = settings
        self.temp_registration_ttl_hours = 24
        self.verification_code_ttl_minutes = 15
        self.max_verification_attempts = 5
        self.lockout_duration_minutes = 15

    def validate_registration_data(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate registration data without writing to database.
        
        Returns: (is_valid, error_message)
        """
        # Validate email
        if not self._is_valid_email(data.get("email", "")):
            return False, "Invalid email format"

        # Validate phone (E.164 format)
        if not self._is_valid_phone(data.get("phone", "")):
            return False, "Invalid phone format"

        # Validate salon name
        salon_name = data.get("salon_name", "").strip()
        if not salon_name or len(salon_name) < 3 or len(salon_name) > 255:
            return False, "Salon name must be 3-255 characters"

        # Validate owner name
        owner_name = data.get("owner_name", "").strip()
        if not owner_name or len(owner_name) < 2 or len(owner_name) > 100:
            return False, "Owner name must be 2-100 characters"

        # Validate password
        password = data.get("password", "")
        is_strong, password_error = self._is_strong_password(password)
        if not is_strong:
            return False, password_error

        # Validate address
        address = data.get("address", "").strip()
        if not address or len(address) < 5 or len(address) > 500:
            return False, "Address must be 5-500 characters"

        # Validate bank account if provided
        if data.get("bank_account"):
            bank_account = data.get("bank_account", "").strip()
            if len(bank_account) < 10 or len(bank_account) > 50:
                return False, "Bank account must be 10-50 characters"

        # Validate referral code if provided
        if data.get("referral_code"):
            referral_code = data.get("referral_code", "").strip()
            if not re.match(r"^[a-zA-Z0-9]+$", referral_code):
                return False, "Referral code must be alphanumeric"

        return True, None

    def check_uniqueness(self, email: str, phone: str, salon_name: str) -> tuple[bool, Optional[str]]:
        """
        Check if email, phone, and salon name are unique.
        
        Returns: (is_unique, error_message)
        """
        # Check email uniqueness
        if User.objects(email=email).first():
            return False, "Email already registered"
        if TempRegistration.objects(email=email).first():
            return False, "Email already in registration process"

        # Check phone uniqueness
        if User.objects(phone=phone).first():
            return False, "Phone already registered"
        if TempRegistration.objects(phone=phone).first():
            return False, "Phone already in registration process"

        # Check salon name uniqueness (case-insensitive)
        if Tenant.objects(name__iexact=salon_name).first():
            return False, "Salon name already taken"

        return True, None

    def generate_subdomain(self, salon_name: str) -> str:
        """
        Generate a unique subdomain from salon name.
        
        Converts salon name to URL-safe format and ensures uniqueness.
        """
        # Convert to lowercase and replace spaces/special chars with hyphens
        subdomain = re.sub(r"[^a-z0-9]+", "-", salon_name.lower()).strip("-")
        
        # Ensure it's not too long (max 63 chars for DNS)
        subdomain = subdomain[:63]

        # Check uniqueness and add suffix if needed
        base_subdomain = subdomain
        counter = 1
        while Tenant.objects(subdomain=subdomain).first() or TempRegistration.objects(subdomain=subdomain).first():
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1

        return subdomain

    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code."""
        return "".join(secrets.choice(string.digits) for _ in range(6))

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def invalidate_sessions_for_email(self, email: str) -> None:
        """Invalidate all active sessions for a given email address."""
        try:
            # Find all users with this email
            users = User.objects(email=email)
            for user in users:
                # Invalidate all active sessions for this user
                Session.objects(user_id=user.id, status="active").update(status="revoked")
                logger.info(f"Invalidated all sessions for user: {user.id}")
        except Exception as e:
            logger.error(f"Error invalidating sessions for email {email}: {e}")
            # Don't fail registration if session invalidation fails

    def create_temp_registration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create temporary registration record.
        
        Returns: temp_registration data with temp_registration_id
        """
        # Generate subdomain and verification code
        subdomain = self.generate_subdomain(data["salon_name"])
        verification_code = self.generate_verification_code()
        password_hash = self.hash_password(data["password"])

        # Calculate expiration times
        now = datetime.utcnow()
        verification_code_expires = now + timedelta(minutes=self.verification_code_ttl_minutes)
        registration_expires = now + timedelta(hours=self.temp_registration_ttl_hours)

        # Create temporary registration (but don't save yet - only save after email is sent)
        temp_reg = TempRegistration(
            email=data["email"],
            phone=data["phone"],
            salon_name=data["salon_name"],
            owner_name=data["owner_name"],
            address=data["address"],
            bank_account=data.get("bank_account"),
            password_hash=password_hash,
            subdomain=subdomain,
            verification_code=verification_code,
            verification_code_expires=verification_code_expires,
            referral_code=data.get("referral_code"),
            expires_at=registration_expires,
        )

        return {
            "temp_registration_id": None,  # Not saved yet
            "temp_reg_object": temp_reg,  # Return the unsaved object
            "email": temp_reg.email,
            "subdomain": temp_reg.subdomain,
            "verification_code": verification_code,  # Return for email sending
            "verification_code_expires": verification_code_expires.isoformat() + "Z",
        }

    def verify_code(self, email: str, code: str) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Verify code and create accounts if valid.
        
        Returns: (success, error_message, account_data)
        """
        # Find temporary registration
        temp_reg = TempRegistration.objects(email=email).first()
        if not temp_reg:
            return False, "Registration not found", None

        # Check if registration is expired
        if temp_reg.is_registration_expired:
            temp_reg.delete()
            return False, "Registration expired. Please register again.", None

        # Check if locked
        if temp_reg.is_locked:
            return False, "Too many failed attempts. Please try again later.", None

        # Check if code is expired
        if temp_reg.is_code_expired:
            return False, "Verification code expired. Please request a new code.", None

        # Check if code is correct
        # Strip whitespace and compare
        stored_code = temp_reg.verification_code.strip() if temp_reg.verification_code else ""
        provided_code = code.strip() if code else ""
        
        if stored_code != provided_code:
            temp_reg.attempt_count += 1
            if temp_reg.attempt_count >= self.max_verification_attempts:
                temp_reg.locked_until = datetime.utcnow() + timedelta(
                    minutes=self.lockout_duration_minutes
                )
            temp_reg.save()
            # Log for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Code mismatch for {email}: stored='{stored_code}' (len={len(stored_code)}), provided='{provided_code}' (len={len(provided_code)})")
            return False, "Invalid verification code", None

        # Code is correct - create accounts
        tenant = None
        user = None
        role = None
        
        try:
            # Create tenant with retry logic for subdomain conflicts
            max_retries = 3
            subdomain = temp_reg.subdomain
            
            for attempt in range(max_retries):
                try:
                    # Default business hours
                    default_business_hours = {
                        "monday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                        "tuesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                        "wednesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                        "thursday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                        "friday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                        "saturday": {"open_time": "10:00", "close_time": "16:00", "is_closed": False},
                        "sunday": {"open_time": "00:00", "close_time": "00:00", "is_closed": True},
                    }

                    tenant = Tenant(
                        name=temp_reg.salon_name,
                        subdomain=subdomain,
                        subscription_tier="trial",  # New users get 30-day trial
                        status="active",
                        is_published=True,
                        address=temp_reg.address,
                        settings={
                            "trial_end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                            "owner_phone": temp_reg.phone,
                            "owner_email": temp_reg.email,
                            "email": temp_reg.email,  # Set business email from owner email
                            "phone": temp_reg.phone,  # Set business phone from owner phone
                            "tax_rate": 0.0,
                            "currency": "NGN",
                            "timezone": "Africa/Lagos",
                            "language": "en",
                            "business_hours": default_business_hours,
                            "notification_email": True,
                            "notification_sms": False,
                            "notification_push": False,
                            "logo_url": None,
                            "primary_color": "#000000",
                            "secondary_color": "#FFFFFF",
                            "appointment_reminder_hours": 24,
                            "allow_online_booking": True,
                            "require_customer_approval": False,
                            "auto_confirm_bookings": True,
                        },
                    )
                    tenant.save()
                    break  # Success, exit retry loop
                except Exception as e:
                    if "E11000" in str(e) and "subdomain" in str(e):
                        # Subdomain conflict, try again with a new one
                        if attempt < max_retries - 1:
                            subdomain = self.generate_subdomain(temp_reg.salon_name)
                            continue
                        else:
                            # Max retries reached, still getting subdomain conflict
                            return False, "Unable to generate unique subdomain. Please try registering again.", None
                    raise  # Re-raise if not a subdomain conflict or max retries reached

            if not tenant:
                return False, "Failed to create tenant after multiple attempts", None

            # Create trial subscription for the tenant
            from app.services.subscription_service import SubscriptionService
            SubscriptionService.create_trial_subscription(str(tenant.id), trial_days=30)

            # Create default roles for the tenant using RBAC service
            from app.services.rbac_service import RBACService
            rbac_service = RBACService()
            rbac_service.create_default_roles(str(tenant.id))

            # Get Owner role for the new user
            role = Role.objects(tenant_id=tenant.id, name="Owner").first()
            if not role:
                # Fallback: create a basic owner role if default roles creation failed
                role = Role(
                    tenant_id=tenant.id,
                    name="Owner",
                    description="Full platform access",
                    permissions=[],
                )
                role.save()

            # Create user with Owner role as default
            user = User(
                tenant_id=tenant.id,
                email=temp_reg.email,
                password_hash=temp_reg.password_hash,
                first_name=temp_reg.owner_name.split()[0],
                last_name=" ".join(temp_reg.owner_name.split()[1:]) if len(temp_reg.owner_name.split()) > 1 else "",
                phone=temp_reg.phone,
                role_ids=[role.id],  # Owner role as default
                status="active",
                mfa_enabled=False,
            )
            user.save()

            # Invalidate any existing sessions for this email (cross-browser awareness)
            # This ensures that if the user was logged in on another browser, they're logged out
            self.invalidate_sessions_for_email(temp_reg.email)

            # Track referral if provided
            if temp_reg.referral_code:
                self._track_referral(temp_reg.referral_code, tenant.id)

            # Delete temporary registration
            temp_reg.delete()

            # Generate full URL
            platform_domain = self.settings.platform_domain
            full_url = f"{tenant.subdomain}.{platform_domain}"

            return True, None, {
                "tenant_id": str(tenant.id),
                "subdomain": tenant.subdomain,
                "full_url": full_url,
                "user_id": str(user.id),
                "email": user.email,
                "owner_name": temp_reg.owner_name,
                "salon_name": temp_reg.salon_name,
                "role_ids": [str(role.id)],  # Owner role as default
            }

        except Exception as e:
            # If account creation fails, temp_reg is NOT deleted
            # User can retry verification or request a new code
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Account creation failed for {email}: {str(e)}")
            return False, f"Failed to create account: {str(e)}", None

    def resend_verification_code(self, email: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Resend verification code to email.
        
        Returns: (success, error_message, verification_code)
        """
        # Find temporary registration
        temp_reg = TempRegistration.objects(email=email).first()
        if not temp_reg:
            return False, "Registration not found", None

        # Check if registration is expired
        if temp_reg.is_registration_expired:
            temp_reg.delete()
            return False, "Registration expired. Please register again.", None

        # Generate new code
        verification_code = self.generate_verification_code()
        now = datetime.utcnow()
        temp_reg.verification_code = verification_code
        temp_reg.verification_code_expires = now + timedelta(minutes=self.verification_code_ttl_minutes)
        temp_reg.attempt_count = 0  # Reset attempts
        temp_reg.locked_until = None  # Clear lock
        temp_reg.save()

        return True, None, verification_code

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format (RFC 5322 simplified)."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format for African numbers."""
        # African country codes: +20-+299 (Egypt, South Africa, Nigeria, Kenya, etc.)
        # Format: +[country code][number] or [country code][number]
        # Minimum 10 digits total (country code + number), maximum 15 digits
        cleaned = phone.replace(" ", "").replace("-", "")
        
        # Check if it starts with + (international format)
        if cleaned.startswith("+"):
            # +[country code][number] - total 10-15 digits
            pattern = r"^\+[1-9]\d{9,14}$"
        else:
            # [country code][number] - total 10-15 digits
            pattern = r"^[1-9]\d{9,14}$"
        
        return bool(re.match(pattern, cleaned))

    def _is_strong_password(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - Maximum 72 bytes (bcrypt limit)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if len(password.encode('utf-8')) > 72:
            return False, "Password must not exceed 72 bytes"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~]", password):
            return False, "Password must contain at least one special character"
        return True, None

    def _track_referral(self, referral_code: str, new_tenant_id: str) -> None:
        """Track referral for analytics."""
        # This would integrate with referral tracking system
        # For now, just update the temp registration record
        pass
