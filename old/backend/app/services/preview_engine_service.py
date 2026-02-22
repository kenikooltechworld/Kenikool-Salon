"""Preview Engine Service for White Label System

Generates live previews of branding configurations with support for multiple page types.
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel

from app.services.theme_engine_service import ThemeEngineService

logger = logging.getLogger(__name__)


class AccessibilityWarning(BaseModel):
    """Accessibility warning for preview"""
    type: str  # "color_contrast", "missing_alt_text", etc.
    severity: str  # "warning", "error"
    message: str
    suggestion: Optional[str] = None


class PreviewResponse(BaseModel):
    """Response containing preview HTML and metadata"""
    html: str
    page_type: str
    tenant_id: str
    generated_at: datetime
    accessibility_warnings: List[AccessibilityWarning] = []
    branding_applied: Dict = {}


class PreviewEngineService:
    """Service for generating live previews of white label branding"""

    def __init__(self):
        """Initialize preview engine service"""
        self.theme_engine = ThemeEngineService()
        self.page_templates = self._load_page_templates()

    def _load_page_templates(self) -> Dict[str, str]:
        """
        Load HTML templates for different page types
        
        Returns:
            Dictionary mapping page types to HTML templates
        """
        return {
            "home": self._get_home_template(),
            "booking": self._get_booking_template(),
            "checkout": self._get_checkout_template(),
        }

    def _get_home_template(self) -> str:
        """Get home page template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home - Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: var(--font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            line-height: 1.6;
            color: #333;
        }
        header {
            background-color: var(--primary-color, #007bff);
            color: white;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            height: 40px;
            width: auto;
        }
        nav {
            display: flex;
            gap: 20px;
        }
        nav a {
            color: white;
            text-decoration: none;
            font-weight: 500;
        }
        nav a:hover {
            opacity: 0.8;
        }
        .hero {
            background: linear-gradient(135deg, var(--primary-color, #007bff), var(--secondary-color, #0056b3));
            color: white;
            padding: 60px 20px;
            text-align: center;
        }
        .hero h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        .hero p {
            font-size: 1.2em;
            margin-bottom: 30px;
        }
        .cta-button {
            background-color: var(--accent-color, #28a745);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .cta-button:hover {
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .feature-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .feature-card h3 {
            color: var(--primary-color, #007bff);
            margin-bottom: 10px;
        }
        footer {
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-container">
            <img src="{{LOGO_URL}}" alt="Logo" class="logo" onerror="this.style.display='none'">
        </div>
        <nav>
            <a href="#home">Home</a>
            <a href="#services">Services</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
        </nav>
    </header>
    
    <section class="hero">
        <h1>{{COMPANY_NAME}}</h1>
        <p>{{TAGLINE}}</p>
        <button class="cta-button">Book Now</button>
    </section>
    
    <section class="features">
        <div class="feature-card">
            <h3>Easy Booking</h3>
            <p>Simple and intuitive booking system</p>
        </div>
        <div class="feature-card">
            <h3>Professional Service</h3>
            <p>Expert staff ready to serve you</p>
        </div>
        <div class="feature-card">
            <h3>Great Prices</h3>
            <p>Competitive pricing for quality service</p>
        </div>
    </section>
    
    <footer>
        <p>&copy; {{COMPANY_NAME}}. All rights reserved.</p>
    </footer>
</body>
</html>"""

    def _get_booking_template(self) -> str:
        """Get booking page template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking - Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: var(--font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            background-color: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: var(--primary-color, #007bff);
            margin-bottom: 30px;
            text-align: center;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 1em;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--primary-color, #007bff);
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }
        .submit-button {
            width: 100%;
            padding: 12px;
            background-color: var(--accent-color, #28a745);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        .submit-button:hover {
            opacity: 0.9;
        }
        .info-box {
            background-color: var(--primary-color, #007bff);
            color: white;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Book Your Appointment at {{COMPANY_NAME}}</h1>
        
        <div class="info-box">
            <p>Select your preferred service and time slot below</p>
        </div>
        
        <form>
            <div class="form-group">
                <label for="service">Service</label>
                <select id="service" required>
                    <option value="">Select a service</option>
                    <option value="haircut">Haircut</option>
                    <option value="coloring">Hair Coloring</option>
                    <option value="styling">Styling</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="date">Preferred Date</label>
                <input type="date" id="date" required>
            </div>
            
            <div class="form-group">
                <label for="time">Preferred Time</label>
                <select id="time" required>
                    <option value="">Select a time</option>
                    <option value="09:00">09:00 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="11:00">11:00 AM</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="name">Your Name</label>
                <input type="text" id="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" required>
            </div>
            
            <button type="submit" class="submit-button">Confirm Booking</button>
        </form>
    </div>
</body>
</html>"""

    def _get_checkout_template(self) -> str:
        """Get checkout page template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: var(--font-family, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif);
            background-color: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: var(--primary-color, #007bff);
            margin-bottom: 30px;
            text-align: center;
        }
        .checkout-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .section {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: var(--primary-color, #007bff);
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .order-summary {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .order-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .order-item:last-child {
            border-bottom: none;
        }
        .total {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            font-weight: 600;
            font-size: 1.1em;
            color: var(--primary-color, #007bff);
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }
        input:focus {
            outline: none;
            border-color: var(--primary-color, #007bff);
        }
        .pay-button {
            width: 100%;
            padding: 12px;
            background-color: var(--accent-color, #28a745);
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
        }
        .pay-button:hover {
            opacity: 0.9;
        }
        @media (max-width: 600px) {
            .checkout-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>Checkout</h1>
    
    <div class="order-summary">
        <h2>Order Summary</h2>
        <div class="order-item">
            <span>Haircut Service</span>
            <span>$50.00</span>
        </div>
        <div class="order-item">
            <span>Hair Coloring</span>
            <span>$75.00</span>
        </div>
        <div class="total">
            <span>Total:</span>
            <span>$125.00</span>
        </div>
    </div>
    
    <div class="checkout-grid">
        <div class="section">
            <h2>Billing Information</h2>
            <div class="form-group">
                <label>Full Name</label>
                <input type="text" placeholder="John Doe">
            </div>
            <div class="form-group">
                <label>Email</label>
                <input type="email" placeholder="john@example.com">
            </div>
            <div class="form-group">
                <label>Address</label>
                <input type="text" placeholder="123 Main St">
            </div>
        </div>
        
        <div class="section">
            <h2>Payment Information</h2>
            <div class="form-group">
                <label>Card Number</label>
                <input type="text" placeholder="1234 5678 9012 3456">
            </div>
            <div class="form-group">
                <label>Expiry Date</label>
                <input type="text" placeholder="MM/YY">
            </div>
            <div class="form-group">
                <label>CVV</label>
                <input type="text" placeholder="123">
            </div>
        </div>
    </div>
    
    <button class="pay-button">Complete Payment</button>
</body>
</html>"""

    async def generate_preview(
        self,
        branding_config: Dict,
        page_type: str = "home",
        tenant_id: str = None,
    ) -> PreviewResponse:
        """
        Generate preview HTML with branding applied
        
        Args:
            branding_config: Dictionary with branding settings
            page_type: Type of page to preview (home, booking, checkout)
            tenant_id: Optional tenant ID for tracking
            
        Returns:
            PreviewResponse with rendered HTML and metadata
        """
        # Validate page type
        if page_type not in self.page_templates:
            raise ValueError(f"Invalid page type: {page_type}. Must be one of: {list(self.page_templates.keys())}")
        
        # Get template
        template = self.page_templates[page_type]
        
        # Replace placeholders
        html = template
        html = html.replace("{{LOGO_URL}}", branding_config.get("logo_url", ""))
        html = html.replace("{{COMPANY_NAME}}", branding_config.get("company_name", "My Business"))
        html = html.replace("{{TAGLINE}}", branding_config.get("tagline", "Welcome to our business"))
        
        # Generate theme CSS
        theme_css = self.theme_engine.generate_complete_theme_css(branding_config)
        
        # Inject CSS into HTML
        html = self.theme_engine.inject_css_into_html(html, theme_css, tenant_id)
        
        # Check for accessibility warnings
        warnings = self._check_accessibility(branding_config)
        
        return PreviewResponse(
            html=html,
            page_type=page_type,
            tenant_id=tenant_id or "default",
            generated_at=datetime.utcnow(),
            accessibility_warnings=warnings,
            branding_applied={
                "primary_color": branding_config.get("primary_color"),
                "secondary_color": branding_config.get("secondary_color"),
                "accent_color": branding_config.get("accent_color"),
                "font_family": branding_config.get("font_family"),
                "company_name": branding_config.get("company_name"),
            }
        )

    def _check_accessibility(self, branding_config: Dict) -> List[AccessibilityWarning]:
        """
        Check branding configuration for accessibility issues
        
        Args:
            branding_config: Dictionary with branding settings
            
        Returns:
            List of accessibility warnings
        """
        warnings = []
        
        # Check color contrast
        if branding_config.get("primary_color") and branding_config.get("secondary_color"):
            contrast = self.theme_engine.validate_color_contrast(
                branding_config["primary_color"],
                branding_config["secondary_color"]
            )
            
            if contrast.get("valid") and not contrast.get("wcag_aa"):
                warnings.append(AccessibilityWarning(
                    type="color_contrast",
                    severity="warning",
                    message=f"Color contrast ratio ({contrast['contrast_ratio']}:1) below WCAG AA standard (4.5:1)",
                    suggestion="Consider using colors with higher contrast for better readability"
                ))
        
        # Check if logo is provided
        if not branding_config.get("logo_url"):
            warnings.append(AccessibilityWarning(
                type="missing_logo",
                severity="warning",
                message="No logo provided",
                suggestion="Add a logo to complete your branding"
            ))
        
        # Check if company name is provided
        if not branding_config.get("company_name"):
            warnings.append(AccessibilityWarning(
                type="missing_company_name",
                severity="warning",
                message="No company name provided",
                suggestion="Add your company name for better branding"
            ))
        
        return warnings

    async def render_preview_component(
        self,
        component: str,
        branding_config: Dict,
        tenant_id: str = None,
    ) -> str:
        """
        Render a specific preview component with branding
        
        Args:
            component: Component name (e.g., "header", "button", "card")
            branding_config: Dictionary with branding settings
            tenant_id: Optional tenant ID
            
        Returns:
            Rendered HTML for the component
        """
        components = {
            "header": self._render_header_component,
            "button": self._render_button_component,
            "card": self._render_card_component,
            "footer": self._render_footer_component,
        }
        
        if component not in components:
            raise ValueError(f"Unknown component: {component}")
        
        renderer = components[component]
        html = renderer(branding_config)
        
        # Generate theme CSS
        theme_css = self.theme_engine.generate_complete_theme_css(branding_config)
        
        # Inject CSS
        html = self.theme_engine.inject_css_into_html(html, theme_css, tenant_id)
        
        return html

    def _render_header_component(self, branding_config: Dict) -> str:
        """Render header component"""
        return f"""<header style="background-color: var(--primary-color, #007bff); color: white; padding: 20px; display: flex; align-items: center; justify-content: space-between;">
    <div class="logo-container">
        <img src="{branding_config.get('logo_url', '')}" alt="Logo" style="height: 40px; width: auto;" onerror="this.style.display='none'">
    </div>
    <h1>{branding_config.get('company_name', 'My Business')}</h1>
</header>"""

    def _render_button_component(self, branding_config: Dict) -> str:
        """Render button component"""
        return f"""<button style="background-color: var(--accent-color, #28a745); color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 1em; cursor: pointer;">
    Click Me
</button>"""

    def _render_card_component(self, branding_config: Dict) -> str:
        """Render card component"""
        return f"""<div style="border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
    <h3 style="color: var(--primary-color, #007bff); margin-bottom: 10px;">Card Title</h3>
    <p>This is a sample card component with your branding applied.</p>
</div>"""

    def _render_footer_component(self, branding_config: Dict) -> str:
        """Render footer component"""
        return f"""<footer style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #ddd;">
    <p>&copy; {branding_config.get('company_name', 'My Business')}. All rights reserved.</p>
</footer>"""

    async def validate_preview_config(
        self,
        branding_config: Dict,
    ) -> List[AccessibilityWarning]:
        """
        Validate preview configuration for issues
        
        Args:
            branding_config: Dictionary with branding settings
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Validate branding config
        validation_result = self.theme_engine.validate_branding_config(branding_config)
        
        # Convert validation errors to warnings
        for error in validation_result.errors:
            warnings.append(AccessibilityWarning(
                type="validation_error",
                severity="error",
                message=error
            ))
        
        # Add validation warnings
        for warning in validation_result.warnings:
            warnings.append(AccessibilityWarning(
                type="validation_warning",
                severity="warning",
                message=warning
            ))
        
        # Add accessibility warnings
        warnings.extend(self._check_accessibility(branding_config))
        
        return warnings
