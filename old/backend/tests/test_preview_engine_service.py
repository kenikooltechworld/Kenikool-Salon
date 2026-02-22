"""Tests for Preview Engine Service"""
import pytest
from app.services.preview_engine_service import (
    PreviewEngineService,
    PreviewResponse,
    AccessibilityWarning,
)


class TestPreviewEngineService:
    """Tests for PreviewEngineService"""

    @pytest.fixture
    def service(self):
        """Create a PreviewEngineService instance"""
        return PreviewEngineService()

    @pytest.fixture
    def basic_branding_config(self):
        """Basic branding configuration for testing"""
        return {
            "company_name": "Test Salon",
            "tagline": "Your beauty destination",
            "primary_color": "#007bff",
            "secondary_color": "#0056b3",
            "accent_color": "#28a745",
            "font_family": "Roboto",
            "logo_url": "https://example.com/logo.png",
        }

    @pytest.fixture
    def minimal_branding_config(self):
        """Minimal branding configuration"""
        return {
            "company_name": "My Business",
        }

    # ============ Preview Generation Tests ============

    @pytest.mark.asyncio
    async def test_generate_preview_home_page(self, service, basic_branding_config):
        """Test generating preview for home page"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="home",
            tenant_id="tenant_123",
        )

        assert isinstance(preview, PreviewResponse)
        assert preview.page_type == "home"
        assert preview.tenant_id == "tenant_123"
        assert "Test Salon" in preview.html
        assert "Your beauty destination" in preview.html
        assert preview.branding_applied["company_name"] == "Test Salon"
        assert preview.branding_applied["primary_color"] == "#007bff"

    @pytest.mark.asyncio
    async def test_generate_preview_booking_page(self, service, basic_branding_config):
        """Test generating preview for booking page"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="booking",
            tenant_id="tenant_123",
        )

        assert preview.page_type == "booking"
        assert "Book Your Appointment" in preview.html
        assert "Test Salon" in preview.html

    @pytest.mark.asyncio
    async def test_generate_preview_checkout_page(self, service, basic_branding_config):
        """Test generating preview for checkout page"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="checkout",
            tenant_id="tenant_123",
        )

        assert preview.page_type == "checkout"
        assert "Checkout" in preview.html
        assert "Order Summary" in preview.html

    @pytest.mark.asyncio
    async def test_generate_preview_invalid_page_type(self, service, basic_branding_config):
        """Test generating preview with invalid page type"""
        with pytest.raises(ValueError, match="Invalid page type"):
            await service.generate_preview(
                branding_config=basic_branding_config,
                page_type="invalid_page",
                tenant_id="tenant_123",
            )

    @pytest.mark.asyncio
    async def test_generate_preview_with_css_variables(self, service, basic_branding_config):
        """Test that CSS variables are injected into preview"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="home",
        )

        assert "--primary-color: #007bff" in preview.html
        assert "--secondary-color: #0056b3" in preview.html
        assert "--accent-color: #28a745" in preview.html
        assert "--font-family: Roboto" in preview.html

    @pytest.mark.asyncio
    async def test_generate_preview_with_minimal_config(self, service, minimal_branding_config):
        """Test generating preview with minimal configuration"""
        preview = await service.generate_preview(
            branding_config=minimal_branding_config,
            page_type="home",
        )

        assert preview.page_type == "home"
        assert "My Business" in preview.html
        assert isinstance(preview.accessibility_warnings, list)

    # ============ Accessibility Warnings Tests ============

    @pytest.mark.asyncio
    async def test_accessibility_warning_missing_logo(self, service, minimal_branding_config):
        """Test accessibility warning for missing logo"""
        preview = await service.generate_preview(
            branding_config=minimal_branding_config,
            page_type="home",
        )

        warnings = preview.accessibility_warnings
        assert len(warnings) > 0
        
        missing_logo_warning = next(
            (w for w in warnings if w.type == "missing_logo"),
            None
        )
        assert missing_logo_warning is not None
        assert missing_logo_warning.severity == "warning"

    @pytest.mark.asyncio
    async def test_accessibility_warning_color_contrast(self, service):
        """Test accessibility warning for poor color contrast"""
        # Use colors with poor contrast
        config = {
            "company_name": "Test",
            "primary_color": "#FFFFFF",  # White
            "secondary_color": "#FFFFCC",  # Very light yellow
        }

        preview = await service.generate_preview(
            branding_config=config,
            page_type="home",
        )

        warnings = preview.accessibility_warnings
        contrast_warning = next(
            (w for w in warnings if w.type == "color_contrast"),
            None
        )
        assert contrast_warning is not None
        assert contrast_warning.severity == "warning"

    @pytest.mark.asyncio
    async def test_no_accessibility_warning_good_contrast(self, service):
        """Test no accessibility warning for good color contrast"""
        config = {
            "company_name": "Test",
            "primary_color": "#000000",  # Black
            "secondary_color": "#FFFFFF",  # White
        }

        preview = await service.generate_preview(
            branding_config=config,
            page_type="home",
        )

        warnings = preview.accessibility_warnings
        contrast_warning = next(
            (w for w in warnings if w.type == "color_contrast"),
            None
        )
        assert contrast_warning is None

    # ============ Component Rendering Tests ============

    @pytest.mark.asyncio
    async def test_render_header_component(self, service, basic_branding_config):
        """Test rendering header component"""
        html = await service.render_preview_component(
            component="header",
            branding_config=basic_branding_config,
            tenant_id="tenant_123",
        )

        assert isinstance(html, str)
        assert "Test Salon" in html
        assert "header" in html.lower()

    @pytest.mark.asyncio
    async def test_render_button_component(self, service, basic_branding_config):
        """Test rendering button component"""
        html = await service.render_preview_component(
            component="button",
            branding_config=basic_branding_config,
        )

        assert isinstance(html, str)
        assert "button" in html.lower()
        assert "--accent-color" in html

    @pytest.mark.asyncio
    async def test_render_card_component(self, service, basic_branding_config):
        """Test rendering card component"""
        html = await service.render_preview_component(
            component="card",
            branding_config=basic_branding_config,
        )

        assert isinstance(html, str)
        assert "Card Title" in html

    @pytest.mark.asyncio
    async def test_render_footer_component(self, service, basic_branding_config):
        """Test rendering footer component"""
        html = await service.render_preview_component(
            component="footer",
            branding_config=basic_branding_config,
        )

        assert isinstance(html, str)
        assert "Test Salon" in html
        assert "footer" in html.lower()

    @pytest.mark.asyncio
    async def test_render_invalid_component(self, service, basic_branding_config):
        """Test rendering invalid component"""
        with pytest.raises(ValueError, match="Unknown component"):
            await service.render_preview_component(
                component="invalid_component",
                branding_config=basic_branding_config,
            )

    # ============ Configuration Validation Tests ============

    @pytest.mark.asyncio
    async def test_validate_preview_config_valid(self, service, basic_branding_config):
        """Test validating valid preview configuration"""
        warnings = await service.validate_preview_config(basic_branding_config)

        # Should have some warnings but no errors
        error_warnings = [w for w in warnings if w.severity == "error"]
        assert len(error_warnings) == 0

    @pytest.mark.asyncio
    async def test_validate_preview_config_invalid_color(self, service):
        """Test validating configuration with invalid color"""
        config = {
            "company_name": "Test",
            "primary_color": "invalid_color",
        }

        warnings = await service.validate_preview_config(config)

        error_warnings = [w for w in warnings if w.severity == "error"]
        assert len(error_warnings) > 0

    @pytest.mark.asyncio
    async def test_validate_preview_config_invalid_css(self, service):
        """Test validating configuration with invalid CSS"""
        config = {
            "company_name": "Test",
            "custom_css": "@import url('https://evil.com/style.css');",
        }

        warnings = await service.validate_preview_config(config)

        error_warnings = [w for w in warnings if w.severity == "error"]
        assert len(error_warnings) > 0

    # ============ Template Loading Tests ============

    def test_page_templates_loaded(self, service):
        """Test that page templates are loaded"""
        assert "home" in service.page_templates
        assert "booking" in service.page_templates
        assert "checkout" in service.page_templates

    def test_home_template_structure(self, service):
        """Test home template has expected structure"""
        template = service.page_templates["home"]
        assert "<!DOCTYPE html>" in template
        assert "{{COMPANY_NAME}}" in template
        assert "{{TAGLINE}}" in template
        assert "{{LOGO_URL}}" in template

    def test_booking_template_structure(self, service):
        """Test booking template has expected structure"""
        template = service.page_templates["booking"]
        assert "<!DOCTYPE html>" in template
        assert "Book Your Appointment" in template
        assert "<form>" in template

    def test_checkout_template_structure(self, service):
        """Test checkout template has expected structure"""
        template = service.page_templates["checkout"]
        assert "<!DOCTYPE html>" in template
        assert "Checkout" in template
        assert "Order Summary" in template

    # ============ Branding Application Tests ============

    @pytest.mark.asyncio
    async def test_branding_applied_metadata(self, service, basic_branding_config):
        """Test that branding applied metadata is correct"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="home",
        )

        assert preview.branding_applied["primary_color"] == "#007bff"
        assert preview.branding_applied["secondary_color"] == "#0056b3"
        assert preview.branding_applied["accent_color"] == "#28a745"
        assert preview.branding_applied["font_family"] == "Roboto"
        assert preview.branding_applied["company_name"] == "Test Salon"

    @pytest.mark.asyncio
    async def test_logo_url_in_preview(self, service, basic_branding_config):
        """Test that logo URL is included in preview"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="home",
        )

        assert "https://example.com/logo.png" in preview.html

    @pytest.mark.asyncio
    async def test_empty_branding_config(self, service):
        """Test generating preview with empty branding config"""
        preview = await service.generate_preview(
            branding_config={},
            page_type="home",
        )

        assert preview.page_type == "home"
        assert isinstance(preview.html, str)
        assert len(preview.html) > 0

    # ============ Response Structure Tests ============

    @pytest.mark.asyncio
    async def test_preview_response_structure(self, service, basic_branding_config):
        """Test PreviewResponse has all required fields"""
        preview = await service.generate_preview(
            branding_config=basic_branding_config,
            page_type="home",
            tenant_id="tenant_123",
        )

        assert hasattr(preview, "html")
        assert hasattr(preview, "page_type")
        assert hasattr(preview, "tenant_id")
        assert hasattr(preview, "generated_at")
        assert hasattr(preview, "accessibility_warnings")
        assert hasattr(preview, "branding_applied")

    @pytest.mark.asyncio
    async def test_accessibility_warning_structure(self, service, minimal_branding_config):
        """Test AccessibilityWarning has all required fields"""
        preview = await service.generate_preview(
            branding_config=minimal_branding_config,
            page_type="home",
        )

        if preview.accessibility_warnings:
            warning = preview.accessibility_warnings[0]
            assert hasattr(warning, "type")
            assert hasattr(warning, "severity")
            assert hasattr(warning, "message")
            assert hasattr(warning, "suggestion")
