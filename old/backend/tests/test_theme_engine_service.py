import pytest
from app.services.theme_engine_service import ThemeEngineService, ValidationResult


class TestThemeEngineService:
    """Tests for ThemeEngineService CSS validation and sanitization"""

    @pytest.fixture
    def service(self):
        """Create a ThemeEngineService instance"""
        return ThemeEngineService()

    # ============ Color Validation Tests ============

    def test_validate_hex_color_valid_6_digit(self, service):
        """Test validation of valid 6-digit hex color"""
        assert service.validate_hex_color("#FF0000") is True
        assert service.validate_hex_color("#00FF00") is True
        assert service.validate_hex_color("#0000FF") is True

    def test_validate_hex_color_valid_3_digit(self, service):
        """Test validation of valid 3-digit hex color"""
        assert service.validate_hex_color("#F00") is True
        assert service.validate_hex_color("#0F0") is True
        assert service.validate_hex_color("#00F") is True

    def test_validate_hex_color_valid_8_digit(self, service):
        """Test validation of valid 8-digit hex color with alpha"""
        assert service.validate_hex_color("#FF0000FF") is True
        assert service.validate_hex_color("#00FF0080") is True

    def test_validate_hex_color_valid_4_digit(self, service):
        """Test validation of valid 4-digit hex color with alpha"""
        assert service.validate_hex_color("#F00F") is True
        assert service.validate_hex_color("#0F08") is True

    def test_validate_hex_color_without_hash(self, service):
        """Test validation of hex color without hash prefix"""
        assert service.validate_hex_color("FF0000") is True
        assert service.validate_hex_color("F00") is True

    def test_validate_hex_color_invalid_format(self, service):
        """Test validation of invalid hex color formats"""
        assert service.validate_hex_color("GGGGGG") is False
        assert service.validate_hex_color("#GGGGGG") is False
        assert service.validate_hex_color("GGGG") is False  # Invalid chars
        assert service.validate_hex_color("") is False
        assert service.validate_hex_color(None) is False

    # ============ CSS Syntax Validation Tests ============

    def test_validate_css_valid_simple(self, service):
        """Test validation of simple valid CSS"""
        css = "body { color: red; }"
        result = service.validate_custom_css(css)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_css_valid_multiple_rules(self, service):
        """Test validation of CSS with multiple rules"""
        css = """
        body { color: red; }
        .button { background-color: blue; padding: 10px; }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_css_empty(self, service):
        """Test validation of empty CSS"""
        result = service.validate_custom_css("")
        assert result.is_valid is True
        assert result.sanitized_css == ""

    def test_validate_css_none(self, service):
        """Test validation of None CSS"""
        result = service.validate_custom_css(None)
        assert result.is_valid is True

    # ============ Dangerous CSS Properties Tests ============

    def test_validate_css_blocks_import(self, service):
        """Test that @import is blocked"""
        css = "@import url('https://example.com/style.css');"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("@import" in error for error in result.errors)

    def test_validate_css_blocks_url_function(self, service):
        """Test that url() function is blocked"""
        css = "body { background: url('https://example.com/image.jpg'); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("url()" in error for error in result.errors)

    def test_validate_css_blocks_expression(self, service):
        """Test that expression() is blocked"""
        css = "width: expression(alert('XSS'));"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("expression()" in error for error in result.errors)

    def test_validate_css_blocks_behavior(self, service):
        """Test that behavior property is blocked"""
        css = "behavior: url(xss.htc);"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("behavior" in error for error in result.errors)

    def test_validate_css_blocks_javascript_protocol(self, service):
        """Test that javascript: protocol is blocked"""
        css = "background: url(javascript:alert('XSS'));"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("javascript:" in error for error in result.errors)

    def test_validate_css_blocks_vbscript_protocol(self, service):
        """Test that vbscript: protocol is blocked"""
        css = "background: url(vbscript:alert('XSS'));"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("vbscript:" in error for error in result.errors)

    def test_validate_css_blocks_script_tags(self, service):
        """Test that script tags are blocked"""
        css = "<script>alert('XSS')</script>"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("script" in error for error in result.errors)

    def test_validate_css_blocks_event_handlers(self, service):
        """Test that event handlers are blocked"""
        css = "onclick=alert('XSS');"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("onclick" in error for error in result.errors)

    # ============ CSS Sanitization Tests ============

    def test_sanitize_css_removes_import(self, service):
        """Test that sanitization removes @import"""
        css = "@import url('https://example.com/style.css'); body { color: red; }"
        sanitized = service.sanitize_css(css)
        assert "@import" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_url_function(self, service):
        """Test that sanitization removes url() functions"""
        css = "body { background: url('https://example.com/image.jpg'); color: red; }"
        sanitized = service.sanitize_css(css)
        assert "url(" not in sanitized or "data:" in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_expression(self, service):
        """Test that sanitization removes expression()"""
        css = "width: expression(alert('XSS')); color: red;"
        sanitized = service.sanitize_css(css)
        assert "expression" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_javascript_protocol(self, service):
        """Test that sanitization removes javascript: protocol"""
        css = "background: url(javascript:alert('XSS')); color: red;"
        sanitized = service.sanitize_css(css)
        assert "javascript:" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_script_tags(self, service):
        """Test that sanitization removes script tags"""
        css = "<script>alert('XSS')</script> body { color: red; }"
        sanitized = service.sanitize_css(css)
        assert "<script>" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_event_handlers(self, service):
        """Test that sanitization removes event handlers"""
        css = "onclick=alert('XSS'); color: red;"
        sanitized = service.sanitize_css(css)
        assert "onclick" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_preserves_safe_properties(self, service):
        """Test that sanitization preserves safe CSS properties"""
        css = """
        body {
            color: red;
            background-color: blue;
            font-size: 14px;
            margin: 10px;
            padding: 5px;
        }
        """
        sanitized = service.sanitize_css(css)
        assert "color: red" in sanitized or "color:red" in sanitized
        assert "background-color: blue" in sanitized or "background-color:blue" in sanitized

    # ============ CSS Size Validation Tests ============

    def test_validate_css_size_within_limit(self, service):
        """Test CSS size validation within limit"""
        css = "body { color: red; }" * 100  # Small CSS
        result = service.validate_custom_css(css)
        assert len(result.warnings) == 0 or not any("size" in w.lower() for w in result.warnings)

    def test_validate_css_size_exceeds_limit(self, service):
        """Test CSS size validation exceeding limit"""
        # Create CSS larger than 50KB
        css = "body { color: red; }" * 3000
        result = service.validate_custom_css(css)
        assert any("size" in w.lower() for w in result.warnings)

    # ============ Color Contrast Tests ============

    def test_validate_color_contrast_valid_colors(self, service):
        """Test color contrast validation with valid colors"""
        result = service.validate_color_contrast("#000000", "#FFFFFF")
        assert result["valid"] is True
        assert result["contrast_ratio"] == 21.0
        assert result["wcag_aa"] is True
        assert result["wcag_aaa"] is True

    def test_validate_color_contrast_wcag_aa_compliant(self, service):
        """Test color contrast that meets WCAG AA"""
        result = service.validate_color_contrast("#000000", "#CCCCCC")
        assert result["valid"] is True
        assert result["wcag_aa"] is True

    def test_validate_color_contrast_wcag_aa_non_compliant(self, service):
        """Test color contrast that doesn't meet WCAG AA"""
        result = service.validate_color_contrast("#FFFFFF", "#EEEEEE")
        assert result["valid"] is True
        assert result["wcag_aa"] is False

    def test_validate_color_contrast_invalid_color_format(self, service):
        """Test color contrast with invalid color format"""
        result = service.validate_color_contrast("GGGGGG", "#FFFFFF")
        assert result["valid"] is False
        assert "Invalid color format" in result["error"]

    def test_validate_color_contrast_3_digit_hex(self, service):
        """Test color contrast with 3-digit hex colors"""
        result = service.validate_color_contrast("#000", "#FFF")
        assert result["valid"] is True
        assert result["contrast_ratio"] == 21.0

    # ============ Theme CSS Generation Tests ============

    def test_generate_theme_css_with_colors(self, service):
        """Test theme CSS generation with colors"""
        config = {
            "primary_color": "#FF0000",
            "secondary_color": "#00FF00",
            "accent_color": "#0000FF"
        }
        css = service.generate_theme_css(config)
        assert "--primary-color: #FF0000" in css
        assert "--secondary-color: #00FF00" in css
        assert "--accent-color: #0000FF" in css

    def test_generate_theme_css_with_font(self, service):
        """Test theme CSS generation with font"""
        config = {
            "font_family": "Arial, sans-serif"
        }
        css = service.generate_theme_css(config)
        assert "--font-family: Arial, sans-serif" in css

    def test_generate_theme_css_empty_config(self, service):
        """Test theme CSS generation with empty config"""
        css = service.generate_theme_css({})
        assert ":root" in css

    # ============ Branding Config Validation Tests ============

    def test_validate_branding_config_valid(self, service):
        """Test validation of valid branding config"""
        config = {
            "primary_color": "#FF0000",
            "secondary_color": "#00FF00",
            "company_name": "My Salon"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True

    def test_validate_branding_config_invalid_color(self, service):
        """Test validation of branding config with invalid color"""
        config = {
            "primary_color": "GGGGGG",
            "company_name": "My Salon"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is False
        assert any("Invalid primary color" in error for error in result.errors)

    def test_validate_branding_config_poor_contrast(self, service):
        """Test validation of branding config with poor color contrast"""
        config = {
            "primary_color": "#FFFFFF",
            "secondary_color": "#EEEEEE"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True
        assert any("contrast" in w.lower() for w in result.warnings)

    def test_validate_branding_config_with_custom_css(self, service):
        """Test validation of branding config with custom CSS"""
        config = {
            "primary_color": "#FF0000",
            "custom_css": "body { color: red; }"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True

    def test_validate_branding_config_with_dangerous_css(self, service):
        """Test validation of branding config with dangerous CSS"""
        config = {
            "primary_color": "#FF0000",
            "custom_css": "@import url('https://example.com/style.css');"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is False
        assert any("@import" in error for error in result.errors)

    # ============ Integration Tests ============

    def test_full_css_validation_workflow(self, service):
        """Test complete CSS validation workflow"""
        # Valid CSS with safe properties
        css = """
        .button {
            background-color: #FF0000;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is True
        assert result.sanitized_css is not None

    def test_full_css_sanitization_workflow(self, service):
        """Test complete CSS sanitization workflow"""
        # CSS with mixed safe and dangerous content
        css = """
        .button {
            background-color: #FF0000;
            color: white;
        }
        @import url('https://example.com/style.css');
        .link {
            color: blue;
        }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert "@import" in str(result.errors)

    def test_sanitize_then_validate(self, service):
        """Test sanitizing CSS and then validating it"""
        css = """
        body { color: red; }
        @import url('https://example.com/style.css');
        """
        sanitized = service.sanitize_css(css)
        result = service.validate_custom_css(sanitized)
        assert result.is_valid is True
        assert "@import" not in sanitized
