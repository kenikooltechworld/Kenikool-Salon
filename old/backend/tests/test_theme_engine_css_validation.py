import pytest
from app.services.theme_engine_service import ThemeEngineService, ValidationResult


class TestCSSValidation:
    """Test CSS validation and sanitization"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return ThemeEngineService()

    # ===== Hex Color Validation Tests =====

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
        assert service.validate_hex_color("#00FF00AA") is True

    def test_validate_hex_color_valid_4_digit(self, service):
        """Test validation of valid 4-digit hex color with alpha"""
        assert service.validate_hex_color("#F00F") is True
        assert service.validate_hex_color("#0F0A") is True

    def test_validate_hex_color_without_hash(self, service):
        """Test validation of hex color without hash"""
        assert service.validate_hex_color("FF0000") is True
        assert service.validate_hex_color("00FF00") is True

    def test_validate_hex_color_invalid_format(self, service):
        """Test validation of invalid hex color formats"""
        assert service.validate_hex_color("GGGGGG") is False
        assert service.validate_hex_color("#GGGGGG") is False
        assert service.validate_hex_color("FF00") is False
        assert service.validate_hex_color("#FF00") is False

    def test_validate_hex_color_empty(self, service):
        """Test validation of empty color"""
        assert service.validate_hex_color("") is False
        assert service.validate_hex_color(None) is False

    # ===== CSS Syntax Validation Tests =====

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
        h1 { font-size: 24px; }
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

    # ===== Dangerous Properties Detection Tests =====

    def test_validate_css_blocks_import(self, service):
        """Test that @import is blocked"""
        css = "@import url('https://example.com/style.css');"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("@import" in error for error in result.errors)

    def test_validate_css_blocks_url_function(self, service):
        """Test that url() function is blocked"""
        css = "body { background: url('https://example.com/bg.jpg'); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("url()" in error for error in result.errors)

    def test_validate_css_blocks_expression(self, service):
        """Test that expression() is blocked"""
        css = "width: expression(document.body.clientWidth);"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("expression()" in error for error in result.errors)

    def test_validate_css_blocks_behavior(self, service):
        """Test that behavior property is blocked"""
        css = "body { behavior: url(xss.htc); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("behavior" in error for error in result.errors)

    def test_validate_css_blocks_moz_binding(self, service):
        """Test that -moz-binding is blocked"""
        css = "body { -moz-binding: url(xss.xml#xss); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("moz-binding" in error for error in result.errors)

    def test_validate_css_blocks_javascript_protocol(self, service):
        """Test that javascript: protocol is blocked"""
        css = "a { background: url(javascript:alert('xss')); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("javascript:" in error for error in result.errors)

    def test_validate_css_blocks_vbscript_protocol(self, service):
        """Test that vbscript: protocol is blocked"""
        css = "a { background: url(vbscript:msgbox('xss')); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("vbscript:" in error for error in result.errors)

    def test_validate_css_blocks_script_tags(self, service):
        """Test that script tags are blocked"""
        css = "<script>alert('xss')</script>"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("script" in error for error in result.errors)

    def test_validate_css_blocks_event_handlers(self, service):
        """Test that event handlers are blocked"""
        css = "body { onclick: alert('xss'); }"
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("onclick" in error for error in result.errors)

    # ===== CSS Sanitization Tests =====

    def test_sanitize_css_removes_import(self, service):
        """Test that sanitization removes @import"""
        css = "@import url('https://example.com/style.css'); body { color: red; }"
        sanitized = service.sanitize_css(css)
        assert "@import" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_url_function(self, service):
        """Test that sanitization removes url() functions"""
        css = "body { background: url('https://example.com/bg.jpg'); color: red; }"
        sanitized = service.sanitize_css(css)
        assert "url(" not in sanitized or "data:" in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_expression(self, service):
        """Test that sanitization removes expression()"""
        css = "width: expression(document.body.clientWidth); color: red;"
        sanitized = service.sanitize_css(css)
        assert "expression(" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_removes_javascript_protocol(self, service):
        """Test that sanitization removes javascript: protocol"""
        css = "a { background: url(javascript:alert('xss')); }"
        sanitized = service.sanitize_css(css)
        assert "javascript:" not in sanitized

    def test_sanitize_css_removes_event_handlers(self, service):
        """Test that sanitization removes event handlers"""
        css = "body { onclick: alert('xss'); color: red; }"
        sanitized = service.sanitize_css(css)
        assert "onclick" not in sanitized
        assert "color: red" in sanitized

    def test_sanitize_css_preserves_valid_properties(self, service):
        """Test that sanitization preserves valid CSS properties"""
        css = """
        body {
            color: red;
            background-color: blue;
            font-size: 14px;
            padding: 10px;
        }
        """
        sanitized = service.sanitize_css(css)
        assert "color: red" in sanitized or "color:red" in sanitized
        assert "background-color: blue" in sanitized or "background-color:blue" in sanitized

    def test_sanitize_css_empty(self, service):
        """Test sanitization of empty CSS"""
        assert service.sanitize_css("") == ""
        assert service.sanitize_css(None) == ""

    # ===== CSS Size Validation Tests =====

    def test_validate_css_size_within_limit(self, service):
        """Test CSS within size limit"""
        css = "body { color: red; }" * 100  # Small CSS
        result = service.validate_custom_css(css)
        assert len([w for w in result.warnings if "size" in w.lower()]) == 0

    def test_validate_css_size_exceeds_limit(self, service):
        """Test CSS exceeding size limit"""
        # Create CSS larger than 50KB
        css = "body { color: red; }" * 3000
        result = service.validate_custom_css(css)
        assert any("size" in w.lower() for w in result.warnings)

    # ===== Color Contrast Tests =====

    def test_validate_color_contrast_valid_colors(self, service):
        """Test color contrast with valid colors"""
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

    def test_validate_color_contrast_invalid_color(self, service):
        """Test color contrast with invalid color"""
        result = service.validate_color_contrast("#GGGGGG", "#000000")
        assert result["valid"] is False
        assert "Invalid color format" in result["error"]

    def test_validate_color_contrast_3_digit_hex(self, service):
        """Test color contrast with 3-digit hex colors"""
        result = service.validate_color_contrast("#000", "#FFF")
        assert result["valid"] is True
        assert result["contrast_ratio"] == 21.0

    # ===== Branding Configuration Validation Tests =====

    def test_validate_branding_config_valid(self, service):
        """Test validation of valid branding configuration"""
        config = {
            "primary_color": "#FF0000",
            "secondary_color": "#0000FF",
            "company_name": "My Company"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_branding_config_invalid_color(self, service):
        """Test validation with invalid color"""
        config = {
            "primary_color": "#GGGGGG",
            "company_name": "My Company"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is False
        assert any("Invalid primary color" in error for error in result.errors)

    def test_validate_branding_config_poor_contrast(self, service):
        """Test validation with poor color contrast"""
        config = {
            "primary_color": "#FFFFFF",
            "secondary_color": "#EEEEEE"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True  # Still valid, but with warning
        assert any("contrast" in w.lower() for w in result.warnings)

    def test_validate_branding_config_with_custom_css(self, service):
        """Test validation with custom CSS"""
        config = {
            "primary_color": "#FF0000",
            "custom_css": "body { color: red; }"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is True

    def test_validate_branding_config_with_dangerous_css(self, service):
        """Test validation with dangerous CSS"""
        config = {
            "primary_color": "#FF0000",
            "custom_css": "@import url('https://example.com/style.css');"
        }
        result = service.validate_branding_config(config)
        assert result.is_valid is False
        assert any("@import" in error for error in result.errors)

    # ===== Theme CSS Generation Tests =====

    def test_generate_theme_css_with_colors(self, service):
        """Test CSS variable generation with colors"""
        config = {
            "primary_color": "#FF0000",
            "secondary_color": "#0000FF",
            "accent_color": "#00FF00"
        }
        css = service.generate_theme_css(config)
        assert "--primary-color: #FF0000" in css
        assert "--secondary-color: #0000FF" in css
        assert "--accent-color: #00FF00" in css
        assert ":root" in css

    def test_generate_theme_css_with_font(self, service):
        """Test CSS variable generation with font"""
        config = {
            "font_family": "Arial, sans-serif"
        }
        css = service.generate_theme_css(config)
        assert "--font-family: Arial, sans-serif" in css

    def test_generate_theme_css_empty_config(self, service):
        """Test CSS variable generation with empty config"""
        css = service.generate_theme_css({})
        assert ":root" in css
        assert "}" in css

    def test_generate_theme_css_partial_config(self, service):
        """Test CSS variable generation with partial config"""
        config = {
            "primary_color": "#FF0000"
        }
        css = service.generate_theme_css(config)
        assert "--primary-color: #FF0000" in css
        assert "--secondary-color" not in css


class TestCSSValidationEdgeCases:
    """Test edge cases and complex scenarios"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return ThemeEngineService()

    def test_validate_css_mixed_valid_and_dangerous(self, service):
        """Test CSS with mix of valid and dangerous properties"""
        css = """
        body { color: red; }
        @import url('https://example.com/style.css');
        .button { background-color: blue; }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is False
        assert any("@import" in error for error in result.errors)

    def test_validate_css_case_insensitive_dangerous_properties(self, service):
        """Test that dangerous properties are detected case-insensitively"""
        css = "@IMPORT url('https://example.com/style.css');"
        result = service.validate_custom_css(css)
        assert result.is_valid is False

    def test_validate_css_with_comments(self, service):
        """Test CSS with comments"""
        css = """
        /* This is a comment */
        body { color: red; }
        /* Another comment */
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is True

    def test_validate_css_with_media_queries(self, service):
        """Test CSS with media queries"""
        css = """
        @media (max-width: 600px) {
            body { font-size: 14px; }
        }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is True

    def test_validate_css_with_keyframes(self, service):
        """Test CSS with keyframes"""
        css = """
        @keyframes slide {
            from { left: 0; }
            to { left: 100px; }
        }
        """
        result = service.validate_custom_css(css)
        assert result.is_valid is True

    def test_sanitize_css_preserves_data_uri(self, service):
        """Test that data URIs are preserved during sanitization"""
        css = "body { background: url(data:image/png;base64,iVBORw0KGgo=); }"
        sanitized = service.sanitize_css(css)
        assert "data:" in sanitized

    def test_validate_color_contrast_with_alpha_channel(self, service):
        """Test color contrast with alpha channel"""
        result = service.validate_color_contrast("#000000FF", "#FFFFFFFF")
        assert result["valid"] is True
        assert result["contrast_ratio"] == 21.0

    def test_validate_branding_config_empty(self, service):
        """Test validation of empty branding config"""
        result = service.validate_branding_config({})
        assert result.is_valid is True
        assert len(result.errors) == 0
