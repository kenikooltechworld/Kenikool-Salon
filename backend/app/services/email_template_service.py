"""Email template service for rendering custom email templates."""

import logging
from typing import Dict, Any, Optional
from jinja2 import Template, TemplateSyntaxError
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Service for managing and rendering custom email templates."""

    @staticmethod
    def get_default_customer_welcome_template() -> str:
        """Get the default customer welcome email template."""
        return """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
    <div style="background: linear-gradient(135deg, {{ primary_color }} 0%, {{ secondary_color }} 100%); padding: 40px 20px; text-align: center;">
        {% if logo_url %}
        <img src="{{ logo_url }}" alt="{{ business_name }}" style="max-width: 150px; margin-bottom: 20px;">
        {% endif %}
        <h1 style="color: white; margin: 0;">Welcome to {{ business_name }}!</h1>
    </div>
    
    <div style="padding: 40px 30px;">
        <p style="font-size: 18px; color: #1f2937;">Hi {{ customer_name }},</p>
        
        <p style="color: #4b5563; line-height: 1.8;">
            We're thrilled to have you join our community! Your customer profile has been successfully created, 
            and you're all set to enjoy our services.
        </p>
        
        <div style="background-color: #f9fafb; border-left: 4px solid {{ primary_color }}; padding: 20px; margin: 25px 0;">
            <h3 style="margin-top: 0; color: #1f2937;">Your Profile Information</h3>
            <p style="color: #6b7280;"><strong>Name:</strong> {{ customer_name }}</p>
            <p style="color: #6b7280;"><strong>Email:</strong> {{ customer_email }}</p>
            <p style="color: #6b7280;"><strong>Phone:</strong> {{ customer_phone }}</p>
        </div>
        
        {% if setup_url %}
        <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 25px 0;">
            <h3 style="margin-top: 0; color: #92400e;">Set Up Your Customer Portal Access</h3>
            <p style="color: #78350f;">
                To access your customer portal and manage your bookings online, please set up your password:
            </p>
            <div style="text-align: center; margin: 20px 0;">
                <a href="{{ setup_url }}" style="display: inline-block; background: #f59e0b; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                    Set Up Password
                </a>
            </div>
            <p style="color: #78350f; font-size: 14px;">
                This link will expire in 7 days. If you need a new link, please contact us.
            </p>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{{ booking_url }}" style="display: inline-block; background: {{ primary_color }}; color: white; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600;">
                Book Your First Appointment
            </a>
        </div>
        
        {% if business_address %}
        <div style="background-color: #f9fafb; padding: 20px; margin: 25px 0;">
            <h3 style="margin-top: 0; color: #1f2937;">Visit Us</h3>
            <p style="color: #6b7280;">{{ business_address }}</p>
            {% if business_phone %}
            <p style="color: #6b7280;"><strong>Phone:</strong> {{ business_phone }}</p>
            {% endif %}
        </div>
        {% endif %}
        
        <p style="color: #4b5563;">
            If you have any questions, don't hesitate to reach out. We're here to help!
        </p>
    </div>
    
    <div style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
        <p style="color: #6b7280; font-size: 14px;"><strong>{{ business_name }}</strong></p>
        {% if business_email %}
        <p style="color: #6b7280; font-size: 14px;">Email: {{ business_email }}</p>
        {% endif %}
    </div>
</div>
"""

    @staticmethod
    def render_customer_welcome_email(tenant_id: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Render customer welcome email using tenant's custom template or default.
        
        Args:
            tenant_id: The tenant ID
            context: Template variables (customer_name, business_name, etc.)
            
        Returns:
            Rendered HTML string or None if error
        """
        try:
            # Get tenant
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.error(f"Tenant not found: {tenant_id}")
                return None
            
            # Get custom template from tenant settings or use default
            tenant_settings = tenant.settings or {}
            custom_template = tenant_settings.get("customer_welcome_email_template", "").strip()
            
            if custom_template:
                # Use custom template
                template_str = custom_template
                logger.info(f"Using custom email template for tenant: {tenant_id}")
            else:
                # Use default template
                template_str = EmailTemplateService.get_default_customer_welcome_template()
                logger.info(f"Using default email template for tenant: {tenant_id}")
            
            # Render template with context
            template = Template(template_str)
            rendered_html = template.render(**context)
            
            return rendered_html
            
        except TemplateSyntaxError as e:
            logger.error(f"Template syntax error for tenant {tenant_id}: {str(e)}")
            # Fallback to default template if custom template has errors
            try:
                template_str = EmailTemplateService.get_default_customer_welcome_template()
                template = Template(template_str)
                return template.render(**context)
            except Exception as fallback_error:
                logger.error(f"Fallback template rendering failed: {str(fallback_error)}")
                return None
                
        except Exception as e:
            logger.error(f"Error rendering email template: {str(e)}")
            return None

    @staticmethod
    def validate_template(template_str: str) -> tuple[bool, Optional[str]]:
        """
        Validate email template syntax.
        
        Args:
            template_str: The template string to validate
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # Try to create a Jinja2 template
            Template(template_str)
            return True, None
        except TemplateSyntaxError as e:
            return False, f"Template syntax error: {str(e)}"
        except Exception as e:
            return False, f"Template validation error: {str(e)}"

    @staticmethod
    def get_available_variables() -> Dict[str, str]:
        """
        Get list of available template variables with descriptions.
        
        Returns:
            Dictionary of variable names and their descriptions
        """
        return {
            "customer_name": "Full name of the customer",
            "customer_email": "Customer's email address",
            "customer_phone": "Customer's phone number",
            "business_name": "Your business name",
            "business_address": "Your business address",
            "business_phone": "Your business phone number",
            "business_email": "Your business email address",
            "logo_url": "URL to your business logo",
            "primary_color": "Your primary brand color (hex code)",
            "secondary_color": "Your secondary brand color (hex code)",
            "booking_url": "URL for customers to book appointments",
            "setup_url": "URL for customers to set up their portal password (only for owner-created customers)",
        }
