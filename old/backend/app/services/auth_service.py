"""
Authentication service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import secrets
import logging

from app.config import settings
from app.database import Database
from app.utils.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, generate_subdomain
)
from app.api.exceptions import (
    BadRequestException, UnauthorizedException,
    ConflictException, NotFoundException
)
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for handling auth business logic"""
    
    @staticmethod
    async def register_user(
        salon_name: str,
        owner_name: str,
        email: str,
        phone: str,
        password: str,
        address: Optional[str] = None,
        bank_account: Optional[Dict] = None,
        referral_code: Optional[str] = None,
        tenant_id_for_referral: Optional[str] = None
    ) -> Dict:
        """
        Register a new salon owner - ONLY saves to DB after email verification
        
        Uses a three-phase approach:
        1. VALIDATION PHASE: Validate all inputs and check for conflicts (no DB writes)
        2. PREPARATION PHASE: Generate tokens and prepare data (no DB writes)
        3. EMAIL VERIFICATION: Send verification email, user saves ONLY after verification
        
        This ensures data is only saved AFTER email verification is confirmed.
        
        Args:
            salon_name: Name of the salon
            owner_name: Name of the owner
            email: Email address
            phone: Phone number
            password: Password
            address: Optional address
            bank_account: Optional bank account details
            referral_code: Optional referral code from URL parameter
            tenant_id_for_referral: Optional tenant ID for referral tracking
        
        Returns:
            Dict with verification_token and message (no user data yet)
        """
        try:
            logger.info(f"=== REGISTRATION START === Email: {email}")
            
            # Use Database class (will use test DB in test mode)
            sync_db = Database.get_db()
            logger.info("Database connection obtained")
            
            # ===== PHASE 1: VALIDATION (NO DATABASE WRITES) =====
            logger.info("Phase 1: Validating registration data...")
            await AuthService._validate_registration(sync_db, email, phone, salon_name)
            logger.info("✓ All validations passed")
            
            # ===== PHASE 2: PREPARE DATA (NO DATABASE WRITES) =====
            logger.info("Phase 2: Preparing registration data...")
            subdomain = await AuthService._generate_unique_subdomain(sync_db, salon_name)
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Hash password for later use
            hashed_password = hash_password(password)
            logger.info("✓ Data preparation complete")
            
            # ===== PHASE 3: STORE TEMPORARY REGISTRATION DATA =====
            logger.info("Phase 3: Storing temporary registration data...")
            
            # Generate 6-digit verification code BEFORE storing
            verification_code = str(secrets.randbelow(1000000)).zfill(6)
            logger.info(f"Generated verification code: {verification_code}")
            
            # Store registration data temporarily (expires in 24 hours)
            temp_registration = {
                "email": email,
                "phone": phone,
                "salon_name": salon_name,
                "owner_name": owner_name,
                "address": address,
                "bank_account": bank_account,
                "hashed_password": hashed_password,
                "subdomain": subdomain,
                "verification_code": verification_code,
                "verification_code_expires": datetime.utcnow() + timedelta(minutes=15),
                "referral_code": referral_code,
                "tenant_id_for_referral": tenant_id_for_referral,
                "created_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24)
            }
            
            # Save to temporary registrations collection
            sync_db.temp_registrations.insert_one(temp_registration)
            logger.info(f"✓ Temporary registration stored with code: {verification_code}")
            
            # ===== PHASE 4: SEND VERIFICATION CODE =====
            logger.info("Phase 4: Sending verification code...")
            
            try:
                await email_service.send_email(
                    to=email,
                    subject="Your Verification Code - Kenikool Salon",
                    html=f"""
                    <html>
                        <body>
                            <h2>Welcome, {owner_name}!</h2>
                            <p>Thank you for registering with Kenikool Salon Management.</p>
                            <p>Your verification code is:</p>
                            <h1 style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #6366f1;">{verification_code}</h1>
                            <p>This code expires in 15 minutes.</p>
                            <p>If you didn't create this account, please ignore this email.</p>
                        </body>
                    </html>
                    """
                )
                logger.info(f"✓ Verification code sent to {email}")
            except Exception as e:
                logger.error(f"⚠ Failed to send verification code: {str(e)}")
                # Clean up temporary registration if email fails
                sync_db.temp_registrations.delete_one({"email": email})
                raise Exception("Failed to send verification code. Please try again.")
            
            logger.info(f"=== REGISTRATION PENDING VERIFICATION === Email: {email}")
            
            return {
                "success": True,
                "message": f"Verification code sent to {email}. Please check your inbox and enter the code.",
                "email": email
            }
            
        except (BadRequestException, UnauthorizedException, ConflictException, NotFoundException) as e:
            logger.warning(f"Registration validation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"=== REGISTRATION ERROR === {type(e).__name__}: {str(e)}")
            logger.error(f"Error details:", exc_info=True)
            raise Exception(f"Registration failed: {str(e)}")
    
    @staticmethod
    async def _validate_registration(sync_db, email: str, phone: str, salon_name: str):
        """Validate registration data"""
        # Check email
        existing_user = sync_db.users.find_one({"email": email})
        if existing_user is not None:
            if not existing_user.get("email_verified", False):
                raise ConflictException(
                    "This email is already registered but not verified. "
                    "Please check your email for the verification link or request a new one."
                )
            else:
                raise ConflictException(
                    "This email address is already registered and verified. "
                    "Please login to your existing account."
                )
        
        # Check phone
        existing_phone = sync_db.users.find_one({"phone": phone})
        if existing_phone is not None:
            raise ConflictException(
                "This phone number is already registered. "
                "Please use a different phone number or login to your existing account."
            )
        
        # Check salon name
        salon_name_lower = salon_name.lower()
        is_branch = any(keyword in salon_name_lower for keyword in ['branch', 'location', 'outlet', 'store'])
        
        existing_salon = sync_db.tenants.find_one({
            "salon_name": {"$regex": f"^{salon_name}$", "$options": "i"}
        })
        
        if existing_salon is not None:
            if is_branch:
                raise ConflictException(
                    f"The salon name '{salon_name}' is already taken. "
                    f"Please choose a different name or add a specific location "
                    f"(e.g., '{salon_name} - Lekki', '{salon_name} - Victoria Island')."
                )
            else:
                raise ConflictException(
                    f"The salon name '{salon_name}' is already taken. "
                    f"Please choose a different name. If this is a branch location, "
                    f"include the area name (e.g., '{salon_name} - Victoria Island Branch')."
                )
    
    @staticmethod
    async def _generate_unique_subdomain(sync_db, salon_name: str) -> str:
        """Generate unique subdomain from salon name"""
        base_subdomain = generate_subdomain(salon_name)
        subdomain = base_subdomain
        counter = 1
        
        while sync_db.tenants.find_one({"subdomain": subdomain}) is not None:
            subdomain = f"{base_subdomain}-{counter}"
            counter += 1
        
        return subdomain
    
    @staticmethod
    async def _create_tenant(
        sync_db, salon_name: str, subdomain: str, owner_name: str,
        phone: str, email: str, address: Optional[str], bank_account: Optional[Dict]
    ) -> str:
        """Create tenant record with 30-day trial"""
        tenant_data = {
            "salon_name": salon_name,
            "name": salon_name,  # For marketplace display
            "subdomain": subdomain,
            "owner_name": owner_name,
            "phone": phone,
            "email": email,
            "address": address,
            "brand_color": "#6366f1",
            "is_active": True,
            "is_published": True,  # Automatically publish to marketplace
            "subscription_plan": "trial",
            "average_rating": 0.0,
            "total_reviews": 0,
            "specialties": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if bank_account:
            tenant_data["bank_account"] = bank_account
        
        result = sync_db.tenants.insert_one(tenant_data)
        tenant_id = str(result.inserted_id)
        
        # Also create a salon document in the salons collection for marketplace display
        salon_data = {
            "tenant_id": tenant_id,
            "name": salon_name,
            "description": f"Welcome to {salon_name}",
            "phone": phone,
            "email": email,
            "address": address or "",
            "location": {
                "city": "",
                "state": "",
                "latitude": 0,
                "longitude": 0,
                "address": address or ""
            },
            "image_url": None,
            "logo_url": None,
            "rating": 0.0,
            "review_count": 0,
            "starting_price": 0,
            "is_published": True,
            "is_active": True,
            "services_count": 0,
            "staff_count": 0,
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        sync_db.salons.insert_one(salon_data)
        logger.info(f"Created salon document for tenant {tenant_id}")
        
        # Create 30-day trial subscription with Enterprise features
        trial_subscription = {
            "tenant_id": tenant_id,
            "plan_id": "trial",
            "plan_name": "30-Day Trial",
            "plan_price": 0,
            "status": "trial",
            "trial_ends_at": datetime.utcnow() + timedelta(days=30),
            "current_period_start": datetime.utcnow(),
            "current_period_end": datetime.utcnow() + timedelta(days=30),
            "cancel_at_period_end": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        sync_db.platform_subscriptions.insert_one(trial_subscription)
        logger.info(f"Created 30-day trial subscription for tenant {tenant_id}")
        
        return tenant_id
    
    @staticmethod
    async def _create_user(
        sync_db, email: str, full_name: str, phone: str, password: str,
        tenant_id: str, verification_token: str, verification_expires: datetime
    ) -> str:
        """Create user record"""
        user_data = {
            "email": email,
            "full_name": full_name,
            "phone": phone,
            "role": "owner",
            "is_active": True,
            "email_verified": settings.TESTING,  # Auto-verify in test mode
            "tenant_id": tenant_id,
            "hashed_password": hash_password(password),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Only add verification token if not in test mode
        if not settings.TESTING:
            user_data["verification_token"] = verification_token
            user_data["verification_token_expires"] = verification_expires
        
        result = sync_db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    async def _rollback_registration(sync_db, user_id: Optional[str], tenant_id: Optional[str]):
        """Rollback registration on failure"""
        try:
            if user_id:
                logger.info(f"Rolling back: Deleting user {user_id}")
                sync_db.users.delete_one({"_id": ObjectId(user_id)})
            if tenant_id:
                logger.info(f"Rolling back: Deleting tenant {tenant_id}")
                sync_db.tenants.delete_one({"_id": ObjectId(tenant_id)})
                # Also delete trial subscription
                sync_db.platform_subscriptions.delete_one({"tenant_id": tenant_id})
            logger.info("Rollback completed successfully")
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {str(rollback_error)}")
    
    @staticmethod
    async def login_user(email: str, password: str) -> Dict:
        """
        Login with email and password
        
        Returns:
            Dict with access_token, refresh_token, token_type, user data, and email_verified status
        """
        db = Database.get_db()
        
        # Find user
        user_doc = db.users.find_one({"email": email})
        if user_doc is None:
            raise UnauthorizedException("Invalid email or password")
        
        # Verify password
        if not verify_password(password, user_doc["hashed_password"]):
            raise UnauthorizedException("Invalid email or password")
        
        # Check active status
        if not user_doc.get("is_active", False):
            raise UnauthorizedException("Account is inactive")
        
        user_id = str(user_doc["_id"])
        tenant_id = user_doc["tenant_id"]
        email_verified = user_doc.get("email_verified", False)
        
        # Update last login
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create tokens
        access_token = create_access_token({"sub": user_id, "tenant_id": tenant_id})
        refresh_token = create_refresh_token({"sub": user_id, "tenant_id": tenant_id})
        
        logger.info(f"User logged in: {email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "email_verified": email_verified,
            "user": {
                "id": user_id,
                "email": user_doc["email"],
                "full_name": user_doc["full_name"],
                "phone": user_doc.get("phone"),
                "role": user_doc["role"],
                "is_active": user_doc["is_active"],
                "tenant_id": tenant_id,
                "created_at": user_doc["created_at"]
            }
        }
    
    @staticmethod
    async def verify_email(code: str) -> Tuple[bool, str]:
        """
        Verify user email with verification code and create user/tenant records
        
        Returns:
            Tuple of (success, message)
        """
        db = Database.get_db()
        
        # Find temporary registration with matching code
        temp_reg = db.temp_registrations.find_one({"verification_code": code})
        if temp_reg is None:
            raise NotFoundException("Invalid verification code")
        
        # Check expiry
        if datetime.utcnow() > temp_reg["verification_code_expires"]:
            # Clean up expired registration
            db.temp_registrations.delete_one({"_id": temp_reg["_id"]})
            raise BadRequestException(
                "Verification code has expired. Please register again."
            )
        
        try:
            logger.info(f"=== EMAIL VERIFICATION START === Email: {temp_reg['email']}")
            
            # Create tenant
            tenant_id = await AuthService._create_tenant(
                db, temp_reg["salon_name"], temp_reg["subdomain"], 
                temp_reg["owner_name"], temp_reg["phone"], temp_reg["email"],
                temp_reg.get("address"), temp_reg.get("bank_account")
            )
            logger.info(f"✓ Tenant created: {tenant_id}")
            
            # Create user with verified email
            user_data = {
                "email": temp_reg["email"],
                "full_name": temp_reg["owner_name"],
                "phone": temp_reg["phone"],
                "role": "owner",
                "is_active": True,
                "email_verified": True,
                "tenant_id": tenant_id,
                "hashed_password": temp_reg["hashed_password"],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = db.users.insert_one(user_data)
            user_id = str(result.inserted_id)
            logger.info(f"✓ User created: {user_id}")
            
            # Track referral if provided
            if temp_reg.get("referral_code") and temp_reg.get("tenant_id_for_referral"):
                try:
                    from app.services.referral_service import ReferralService
                    ReferralService.track_referral(
                        tenant_id=temp_reg["tenant_id_for_referral"],
                        referral_code=temp_reg["referral_code"],
                        referred_client_id=user_id
                    )
                    logger.info(f"✓ Referral tracked")
                except Exception as e:
                    logger.warning(f"⚠ Failed to track referral: {str(e)}")
            
            # Delete temporary registration
            db.temp_registrations.delete_one({"_id": temp_reg["_id"]})
            logger.info(f"=== EMAIL VERIFICATION SUCCESS === User: {user_id}")
            
            return True, "Email verified successfully! Your account is now active. You can log in now."
            
        except Exception as e:
            logger.error(f"Email verification failed: {str(e)}", exc_info=True)
            raise BadRequestException(f"Failed to complete registration: {str(e)}")
    
    @staticmethod
    async def resend_verification(email: str) -> Tuple[bool, str]:
        """
        Resend verification code
        
        Returns:
            Tuple of (success, message)
        """
        db = Database.get_db()
        
        # Check if email exists in temp_registrations (pending verification)
        temp_reg = db.temp_registrations.find_one({"email": email})
        if temp_reg is None:
            raise NotFoundException("No pending registration found with this email address")
        
        # Check if already verified (in users collection)
        user_doc = db.users.find_one({"email": email})
        if user_doc and user_doc.get("email_verified", False):
            raise BadRequestException("Email is already verified. You can log in now.")
        
        # Generate new code
        verification_code = str(secrets.randbelow(1000000)).zfill(6)
        
        # Update temporary registration
        db.temp_registrations.update_one(
            {"_id": temp_reg["_id"]},
            {
                "$set": {
                    "verification_code": verification_code,
                    "verification_code_expires": datetime.utcnow() + timedelta(minutes=15),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send email
        try:
            await email_service.send_email(
                to=email,
                subject="Your Verification Code - Kenikool Salon",
                html=f"""
                <html>
                    <body>
                        <h2>Email Verification</h2>
                        <p>Your verification code is:</p>
                        <h1 style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #6366f1;">{verification_code}</h1>
                        <p>This code expires in 15 minutes.</p>
                    </body>
                </html>
                """
            )
            logger.info(f"Verification code resent to {email}")
            return True, "Verification code sent! Please check your inbox."
        except Exception as e:
            logger.error(f"Failed to send verification code: {str(e)}")
            raise Exception("Failed to send verification code. Please try again.")
    
    @staticmethod
    async def forgot_password(email: str) -> Tuple[bool, str]:
        """
        Generate password reset token and send email
        
        Returns:
            Tuple of (success, message)
        """
        db = Database.get_db()
        
        user_doc = db.users.find_one({"email": email})
        
        # Don't reveal if email exists
        if user_doc is None:
            return True, "If an account exists with this email, a password reset link has been sent."
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        # Update user
        db.users.update_one(
            {"_id": user_doc["_id"]},
            {
                "$set": {
                    "reset_token": reset_token,
                    "reset_token_expires": reset_expires,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send email
        try:
            await email_service.send_email(
                to=email,
                subject="Password Reset Request",
                html=f"""
                <html>
                    <body>
                        <h2>Password Reset</h2>
                        <p>Click the link below to reset your password:</p>
                        <p><a href="{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}">Reset Password</a></p>
                        <p>This link expires in 1 hour.</p>
                        <p>If you didn't request this, please ignore this email.</p>
                    </body>
                </html>
                """
            )
            logger.info(f"Password reset email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
        
        return True, "If an account exists with this email, a password reset link has been sent."
    
    @staticmethod
    async def reset_password(token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using reset token
        
        Returns:
            Tuple of (success, message)
        """
        db = Database.get_db()
        
        user_doc = db.users.find_one({"reset_token": token})
        if user_doc is None:
            raise NotFoundException("Invalid or expired reset token")
        
        # Check expiry
        if user_doc.get("reset_token_expires"):
            if datetime.utcnow() > user_doc["reset_token_expires"]:
                raise BadRequestException("Reset token has expired. Please request a new one.")
        
        # Update password
        db.users.update_one(
            {"_id": user_doc["_id"]},
            {
                "$set": {
                    "hashed_password": hash_password(new_password),
                    "updated_at": datetime.utcnow()
                },
                "$unset": {
                    "reset_token": "",
                    "reset_token_expires": ""
                }
            }
        )
        
        logger.info(f"Password reset for user: {user_doc['email']}")
        return True, "Password reset successfully! You can now log in with your new password."
    
    @staticmethod
    async def refresh_token(refresh_token_str: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token_str: The refresh token from the request
        
        Returns:
            Dict with new access_token, refresh_token, token_type, and user data
        """
        from app.utils.security import decode_token
        
        try:
            # Decode refresh token
            payload = decode_token(refresh_token_str)
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            
            if not user_id or not tenant_id:
                raise UnauthorizedException("Invalid refresh token")
            
            db = Database.get_db()
            
            # Get user
            user_doc = db.users.find_one({"_id": ObjectId(user_id)})
            if user_doc is None:
                raise UnauthorizedException("User not found")
            
            # Check active status
            if not user_doc.get("is_active", False):
                raise UnauthorizedException("Account is inactive")
            
            # Create new tokens
            access_token = create_access_token({"sub": user_id, "tenant_id": tenant_id})
            new_refresh_token = create_refresh_token({"sub": user_id, "tenant_id": tenant_id})
            
            logger.info(f"Token refreshed for user: {user_doc['email']}")
            
            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": user_id,
                    "email": user_doc["email"],
                    "full_name": user_doc["full_name"],
                    "phone": user_doc.get("phone"),
                    "role": user_doc["role"],
                    "is_active": user_doc["is_active"],
                    "tenant_id": tenant_id,
                    "created_at": user_doc["created_at"]
                }
            }
            
        except UnauthorizedException:
            raise
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise UnauthorizedException("Invalid or expired refresh token")


# Singleton instance
auth_service = AuthService()
