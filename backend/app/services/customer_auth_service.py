"""Customer Authentication Service"""
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import bcrypt
from jose import jwt, JWTError
from app.models.customer import Customer
from app.config import settings


class CustomerAuthService:
    """Service for customer authentication"""
    
    SECRET_KEY = settings.secret_key
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(customer: Customer) -> str:
        """Create JWT access token for customer"""
        expire = datetime.utcnow() + timedelta(minutes=CustomerAuthService.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(customer.id),
            "email": customer.email,
            "tenant_id": str(customer.tenant_id),
            "type": "customer",
            "exp": expire
        }
        encoded_jwt = jwt.encode(
            to_encode,
            CustomerAuthService.SECRET_KEY,
            algorithm=CustomerAuthService.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                CustomerAuthService.SECRET_KEY,
                algorithms=[CustomerAuthService.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def register_customer(
        tenant_id: ObjectId,
        email: str,
        phone: str,
        password: str,
        first_name: str,
        last_name: str
    ) -> Customer:
        """Register a new customer account"""
        # Check if customer already exists
        existing = Customer.objects(tenant_id=tenant_id, email=email).first()
        if existing and existing.password_hash:
            raise ValueError("Customer account already exists")
        
        # If customer exists as guest, upgrade to registered account
        if existing:
            existing.password_hash = CustomerAuthService.hash_password(password)
            existing.first_name = first_name
            existing.last_name = last_name
            existing.phone = phone
            existing.is_guest = False
            existing.updated_at = datetime.utcnow()
            existing.save()
            return existing
        
        # Create new customer
        customer = Customer(
            tenant_id=tenant_id,
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password_hash=CustomerAuthService.hash_password(password),
            is_guest=False,
            email_verified=False,
            phone_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        customer.save()
        return customer
    
    @staticmethod
    def authenticate_customer(
        tenant_id: ObjectId,
        email: str,
        password: str
    ) -> Optional[Customer]:
        """Authenticate customer with email and password"""
        customer = Customer.objects(
            tenant_id=tenant_id,
            email=email,
            is_guest=False
        ).first()
        
        if not customer or not customer.password_hash:
            return None
        
        if not CustomerAuthService.verify_password(password, customer.password_hash):
            return None
        
        # Update last login
        customer.last_login = datetime.utcnow()
        customer.save()
        
        return customer
    
    @staticmethod
    def send_verification_email(customer: Customer):
        """Send email verification link to customer"""
        from app.tasks import send_email
        from app.services.email_template_service import EmailTemplateService
        from app.models.tenant import Tenant

        token = jwt.encode(
            {"sub": str(customer.id), "type": "email_verification", "exp": datetime.utcnow() + timedelta(hours=24)},
            CustomerAuthService.SECRET_KEY,
            algorithm=CustomerAuthService.ALGORITHM,
        )

        tenant = Tenant.objects(id=customer.tenant_id).first()
        business_email = tenant.settings.get("email", tenant.email) if tenant.settings else tenant.email

        verification_url = f"/public/verify-email/{token}"

        email_context = {
            "customer_email": customer.email,
            "business_email": business_email,
            "verification_url": verification_url,
        }

        rendered_html = EmailTemplateService.render_customer_welcome_email(
            str(customer.tenant_id), email_context
        )

        run_in_background(send_email,
            to=customer.email,
            subject="Verify your email address",
            template=rendered_html or "<p>Please verify your email.</p>",
            context=email_context,
        )
    
    @staticmethod
    def verify_email_token(token: str) -> bool:
        """Verify email verification token and mark customer as verified"""
        payload = CustomerAuthService.decode_token(token)
        if not payload or payload.get("type") != "email_verification":
            return False

        customer_id = payload.get("sub")
        if not customer_id:
            return False

        customer = Customer.objects(id=ObjectId(customer_id)).first()
        if not customer:
            return False

        customer.email_verified = True
        customer.updated_at = datetime.utcnow()
        customer.save()
        return True
    
    @staticmethod
    def get_customer_from_token(token: str, tenant_id: ObjectId) -> Optional[Customer]:
        """Get customer from JWT token"""
        payload = CustomerAuthService.decode_token(token)
        if not payload or payload.get("type") != "customer":
            return None
        
        customer_id = payload.get("sub")
        if not customer_id:
            return None
        
        customer = Customer.objects(
            id=ObjectId(customer_id),
            tenant_id=tenant_id
        ).first()
        
        return customer


