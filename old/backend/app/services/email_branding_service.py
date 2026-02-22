"""
Email Branding Service for applying white label branding to email templates
"""
import re
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.white_label import WhiteLabelConfig
import logging

logger = logging.getLogger(__name__)


class EmailBrandingService:
    """Service for applying white label branding to email templates"""

    def __init__(self):
        pass

    async def apply_branding_to_template(
        self,
        template_name: str,
        config: WhiteLabelConfig,
        data: Dict[str, Any],
    ) -> str:
        """
        Apply white label branding to an email template
        
        Args:
            template_name: Name of the template (e.g., 'verification', 'password_reset')
            config: White label configuration
            data: Template data (e.g., user_name, verification_url)
        
        Returns:
            Branded HTML email template
        """
        try:
            # Get base template
            template_html = self._get_base_template(template_name, data)
            
            # Apply branding
            branded_html = self._apply_branding(template_html, config, data)
            
            return branded_html
        except Exception as e:
            logger.error(f"Error applying branding to template {template_name}: {str(e)}")
            return template_html

    def _get_base_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Get base email template"""
        if template_name == "verification":
            return self._get_verification_template(data)
        elif template_name == "password_reset":
            return self._get_password_reset_template(data)
        elif template_name == "booking_confirmation":
            return self._get_booking_confirmation_template(data)
        elif template_name == "booking_reminder":
            return self._get_booking_reminder_template(data)
        else:
            return ""

    def _get_verification_template(self, data: Dict[str, Any]) -> str:
        """Get verification email template"""
        user_name = data.get("user_name", "User")
        verification_url = data.get("verification_url", "")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px 8px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Kenikool Salon</h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Welcome, {user_name}!</h2>
                                    <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Thank you for registering with Kenikool Salon Management Platform. We're excited to have you on board!
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        To complete your registration and start using your salon management dashboard, please verify your email address by clicking the button below:
                                    </p>
                                    
                                    <!-- Button -->
                                    <table role="presentation" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 6px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
                                                <a href="{verification_url}" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px;">
                                                    Verify Email Address
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 20px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        Or copy and paste this link into your browser:
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #6366f1; font-size: 14px; word-break: break-all;">
                                        {verification_url}
                                    </p>
                                    
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        This verification link will expire in 24 hours.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        If you didn't create an account with Kenikool, please ignore this email.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        © {datetime.now().year} Kenikool Salon Management. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        Lagos, Nigeria
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _get_password_reset_template(self, data: Dict[str, Any]) -> str:
        """Get password reset email template"""
        user_name = data.get("user_name", "User")
        reset_url = data.get("reset_url", "")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px 8px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Kenikool Salon</h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Password Reset Request</h2>
                                    <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Hi {user_name},
                                    </p>
                                    <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        We received a request to reset your password for your Kenikool Salon Management account.
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Click the button below to reset your password:
                                    </p>
                                    
                                    <!-- Button -->
                                    <table role="presentation" style="margin: 0 auto;">
                                        <tr>
                                            <td style="border-radius: 6px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);">
                                                <a href="{reset_url}" style="display: inline-block; padding: 16px 40px; color: #ffffff; text-decoration: none; font-size: 16px; font-weight: bold; border-radius: 6px;">
                                                    Reset Password
                                                </a>
                                            </td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 30px 0 20px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        Or copy and paste this link into your browser:
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #6366f1; font-size: 14px; word-break: break-all;">
                                        {reset_url}
                                    </p>
                                    
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        This password reset link will expire in 1 hour.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        © {datetime.now().year} Kenikool Salon Management. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        Lagos, Nigeria
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _get_booking_confirmation_template(self, data: Dict[str, Any]) -> str:
        """Get booking confirmation email template"""
        client_name = data.get("client_name", "Client")
        service_name = data.get("service_name", "Service")
        booking_date = data.get("booking_date", "")
        booking_time = data.get("booking_time", "")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Booking Confirmation</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px 8px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Kenikool Salon</h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Booking Confirmed!</h2>
                                    <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Hi {client_name},
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Your booking has been confirmed. Here are the details:
                                    </p>
                                    
                                    <!-- Booking Details -->
                                    <table role="presentation" style="width: 100%; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #e5e7eb; border-radius: 6px;">
                                        <tr style="background-color: #f9fafb;">
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Service</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{service_name}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Date</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{booking_date}</td>
                                        </tr>
                                        <tr style="background-color: #f9fafb;">
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Time</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{booking_time}</td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        If you need to reschedule or cancel, please contact us as soon as possible.
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        © {datetime.now().year} Kenikool Salon Management. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        Lagos, Nigeria
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _get_booking_reminder_template(self, data: Dict[str, Any]) -> str:
        """Get booking reminder email template"""
        client_name = data.get("client_name", "Client")
        service_name = data.get("service_name", "Service")
        booking_date = data.get("booking_date", "")
        booking_time = data.get("booking_time", "")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Booking Reminder</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
            <table role="presentation" style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <!-- Header -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 8px 8px 0 0;">
                                    <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Kenikool Salon</h1>
                                </td>
                            </tr>
                            
                            <!-- Content -->
                            <tr>
                                <td style="padding: 40px;">
                                    <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px;">Booking Reminder</h2>
                                    <p style="margin: 0 0 20px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        Hi {client_name},
                                    </p>
                                    <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                        This is a reminder about your upcoming booking:
                                    </p>
                                    
                                    <!-- Booking Details -->
                                    <table role="presentation" style="width: 100%; border-collapse: collapse; margin-bottom: 30px; border: 1px solid #e5e7eb; border-radius: 6px;">
                                        <tr style="background-color: #f9fafb;">
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Service</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{service_name}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Date</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{booking_date}</td>
                                        </tr>
                                        <tr style="background-color: #f9fafb;">
                                            <td style="padding: 12px 16px; font-weight: bold; color: #1f2937;">Time</td>
                                            <td style="padding: 12px 16px; color: #4b5563;">{booking_time}</td>
                                        </tr>
                                    </table>
                                    
                                    <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                        We look forward to seeing you!
                                    </p>
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px; background-color: #f9fafb; border-radius: 0 0 8px 8px; border-top: 1px solid #e5e7eb;">
                                    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        © {datetime.now().year} Kenikool Salon Management. All rights reserved.
                                    </p>
                                    <p style="margin: 0; color: #6b7280; font-size: 12px; text-align: center;">
                                        Lagos, Nigeria
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

    def _apply_branding(
        self,
        html: str,
        config: WhiteLabelConfig,
        data: Dict[str, Any],
    ) -> str:
        """Apply white label branding to HTML template"""
        branded_html = html
        
        # Replace company name
        if config.branding.company_name:
            branded_html = branded_html.replace(
                "Kenikool Salon",
                config.branding.company_name
            )
        
        # Replace primary color (gradient)
        if config.branding.primary_color:
            primary_color = config.branding.primary_color
            secondary_color = config.branding.secondary_color or primary_color
            
            # Replace gradient with primary color
            gradient = f"linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%)"
            branded_html = re.sub(
                r"linear-gradient\(135deg, #[0-9a-fA-F]{6} 0%, #[0-9a-fA-F]{6} 100%\)",
                gradient,
                branded_html
            )
        
        # Replace logo if available
        if config.branding.logo_file or config.branding.logo_url:
            logo_url = config.branding.logo_file or config.branding.logo_url
            # Add logo image after company name in header
            logo_html = f'<img src="{logo_url}" alt="Logo" style="max-width: 100px; height: auto; margin-bottom: 10px;">'
            branded_html = branded_html.replace(
                f"<h1 style=\"margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;\">{config.branding.company_name or 'Kenikool Salon'}</h1>",
                f"{logo_html}<h1 style=\"margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;\">{config.branding.company_name or 'Kenikool Salon'}</h1>"
            )
        
        # Replace footer information
        footer_text = f"© {datetime.now().year} {config.branding.company_name or 'Kenikool Salon Management'}. All rights reserved."
        branded_html = re.sub(
            r"© \d+ Kenikool Salon Management\. All rights reserved\.",
            footer_text,
            branded_html
        )
        
        # Add custom support information if available
        if config.features.custom_support_email or config.features.custom_support_phone:
            support_info = ""
            if config.features.custom_support_email:
                support_info += f"Email: {config.features.custom_support_email}<br>"
            if config.features.custom_support_phone:
                support_info += f"Phone: {config.features.custom_support_phone}"
            
            # Add support info before footer
            branded_html = branded_html.replace(
                "Lagos, Nigeria",
                f"{support_info}<br>Lagos, Nigeria"
            )
        
        # Add custom terms/privacy URLs if available
        if config.features.custom_terms_url or config.features.custom_privacy_url:
            links = []
            if config.features.custom_terms_url:
                links.append(f'<a href="{config.features.custom_terms_url}" style="color: #6366f1; text-decoration: none;">Terms</a>')
            if config.features.custom_privacy_url:
                links.append(f'<a href="{config.features.custom_privacy_url}" style="color: #6366f1; text-decoration: none;">Privacy</a>')
            
            links_html = " | ".join(links)
            branded_html = branded_html.replace(
                "Lagos, Nigeria",
                f"{links_html}<br>Lagos, Nigeria"
            )
        
        # Hide platform branding if configured
        if config.features.hide_powered_by:
            branded_html = re.sub(
                r"Powered by.*?<br>",
                "",
                branded_html,
                flags=re.IGNORECASE
            )
        
        return branded_html

    async def get_branded_from_address(self, config: WhiteLabelConfig) -> str:
        """
        Get the from address for branded emails
        
        Args:
            config: White label configuration
        
        Returns:
            Email from address (custom support email or default)
        """
        if config.features.custom_support_email:
            company_name = config.branding.company_name or "Salon"
            return f"{company_name} <{config.features.custom_support_email}>"
        
        # Return default
        return "Kenikool Salon <noreply@kenikool.com>"

    async def get_branded_subject(
        self,
        base_subject: str,
        config: WhiteLabelConfig
    ) -> str:
        """
        Get a branded email subject
        
        Args:
            base_subject: Base subject line
            config: White label configuration
        
        Returns:
            Branded subject line with company name
        """
        if config.branding.company_name and config.branding.company_name not in base_subject:
            return f"{base_subject} - {config.branding.company_name}"
        return base_subject

    async def apply_branding_to_html(
        self,
        html: str,
        config: WhiteLabelConfig
    ) -> str:
        """
        Apply white label branding to raw HTML
        
        Args:
            html: HTML content
            config: White label configuration
        
        Returns:
            Branded HTML
        """
        return self._apply_branding(html, config, {})

    async def validate_email_domain(self, domain: str) -> Dict[str, Any]:
        """
        Validate email domain configuration
        
        Args:
            domain: Email domain to validate
        
        Returns:
            Validation result with SPF and DKIM status
        """
        import dns.resolver
        import dns.exception
        
        result = {
            "domain": domain,
            "valid": False,
            "spf_configured": False,
            "dkim_configured": False,
            "dmarc_configured": False,
            "spf_record": None,
            "dkim_record": None,
            "dmarc_record": None,
            "issues": [],
            "warnings": [],
            "recommendations": [],
        }
        
        try:
            # Validate domain format
            if not self._is_valid_domain(domain):
                result["issues"].append("Invalid domain format")
                return result
            
            # Check SPF record
            try:
                spf_records = dns.resolver.resolve(domain, "TXT")
                for record in spf_records:
                    record_str = str(record)
                    if "v=spf1" in record_str:
                        result["spf_configured"] = True
                        result["spf_record"] = record_str
                        break
                
                if not result["spf_configured"]:
                    result["issues"].append("SPF record not found")
                    result["recommendations"].append(
                        "Add an SPF record to authorize email sending from your domain"
                    )
            except dns.exception.DNSException as e:
                result["issues"].append(f"SPF check failed: {str(e)}")
                result["recommendations"].append(
                    "Ensure your domain's DNS is properly configured"
                )
            except Exception as e:
                result["issues"].append(f"SPF check failed: {str(e)}")
            
            # Check DKIM record (try common selectors)
            dkim_selectors = ["default", "selector1", "selector2", "k1", "google"]
            dkim_found = False
            for selector in dkim_selectors:
                try:
                    dkim_domain = f"{selector}._domainkey.{domain}"
                    dkim_records = dns.resolver.resolve(dkim_domain, "TXT")
                    if dkim_records:
                        result["dkim_configured"] = True
                        result["dkim_record"] = f"{selector}._domainkey.{domain}"
                        dkim_found = True
                        break
                except dns.exception.DNSException:
                    continue
                except Exception:
                    continue
            
            if not dkim_found:
                result["warnings"].append(
                    "DKIM record not found for common selectors"
                )
                result["recommendations"].append(
                    "Configure DKIM for your email domain to improve deliverability"
                )
            
            # Check DMARC record
            try:
                dmarc_domain = f"_dmarc.{domain}"
                dmarc_records = dns.resolver.resolve(dmarc_domain, "TXT")
                for record in dmarc_records:
                    record_str = str(record)
                    if "v=DMARC1" in record_str:
                        result["dmarc_configured"] = True
                        result["dmarc_record"] = record_str
                        break
                
                if not result["dmarc_configured"]:
                    result["warnings"].append("DMARC record not found")
                    result["recommendations"].append(
                        "Add a DMARC policy to protect your domain from spoofing"
                    )
            except dns.exception.DNSException:
                result["warnings"].append("DMARC record not found")
                result["recommendations"].append(
                    "Add a DMARC policy to protect your domain from spoofing"
                )
            except Exception as e:
                result["warnings"].append(f"DMARC check failed: {str(e)}")
            
            # Domain is valid if at least SPF is configured
            # DKIM and DMARC are recommended but not required
            result["valid"] = result["spf_configured"]
            
            if not result["valid"]:
                result["issues"].append(
                    "Email domain is not properly configured for sending"
                )
            else:
                # Add success message
                if result["dkim_configured"] and result["dmarc_configured"]:
                    result["recommendations"].append(
                        "Your email domain is fully configured with SPF, DKIM, and DMARC"
                    )
                elif result["dkim_configured"]:
                    result["recommendations"].append(
                        "Your email domain has SPF and DKIM configured. Consider adding DMARC"
                    )
                else:
                    result["recommendations"].append(
                        "Your email domain has SPF configured. Consider adding DKIM and DMARC"
                    )
            
        except Exception as e:
            result["issues"].append(f"Validation error: {str(e)}")
            logger.error(f"Error validating email domain {domain}: {str(e)}")
        
        return result

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        domain_pattern = r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
        return bool(re.match(domain_pattern, domain, re.IGNORECASE))


# Singleton instance
email_branding_service = EmailBrandingService()
