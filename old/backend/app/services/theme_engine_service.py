import re
import logging
from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel
import cssutils

logger = logging.getLogger(__name__)

# Suppress cssutils warnings
cssutils.log.setLevel(logging.ERROR)


class ValidationResult(BaseModel):
    """Result of CSS validation"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    sanitized_css: Optional[str] = None


class CSSValidationError(Exception):
    """Raised when CSS validation fails"""
    pass


class ThemeEngineService:
    """Service for managing theme and CSS for white-label configurations"""

    # Dangerous CSS properties that should be blocked
    DANGEROUS_PROPERTIES = {
        "@import",
        "behavior",
        "expression",
        "-moz-binding",
        "-webkit-binding",
    }

    # Dangerous CSS at-rules
    DANGEROUS_AT_RULES = {
        "@import",
        "@namespace",
        "@supports",
        "@document",
        "@-moz-document",
    }

    # Safe CSS properties (whitelist approach)
    SAFE_PROPERTIES = {
        # Colors
        "color",
        "background-color",
        "border-color",
        "outline-color",
        "text-shadow",
        "box-shadow",
        # Typography
        "font-family",
        "font-size",
        "font-weight",
        "font-style",
        "line-height",
        "letter-spacing",
        "text-align",
        "text-decoration",
        "text-transform",
        # Spacing
        "margin",
        "margin-top",
        "margin-right",
        "margin-bottom",
        "margin-left",
        "padding",
        "padding-top",
        "padding-right",
        "padding-bottom",
        "padding-left",
        # Layout
        "display",
        "width",
        "height",
        "max-width",
        "max-height",
        "min-width",
        "min-height",
        "position",
        "top",
        "right",
        "bottom",
        "left",
        "z-index",
        "float",
        "clear",
        "flex",
        "flex-direction",
        "flex-wrap",
        "justify-content",
        "align-items",
        "gap",
        # Borders
        "border",
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
        "border-radius",
        "border-width",
        "border-style",
        # Background
        "background",
        "background-image",
        "background-size",
        "background-position",
        "background-repeat",
        "background-attachment",
        # Effects
        "opacity",
        "transform",
        "transition",
        "animation",
        "filter",
        # Visibility
        "visibility",
        "overflow",
        "overflow-x",
        "overflow-y",
        "cursor",
        # Text
        "white-space",
        "word-wrap",
        "word-break",
        "text-overflow",
    }

    # Maximum CSS file size (50KB)
    MAX_CSS_SIZE = 50 * 1024

    @staticmethod
    def validate_hex_color(color: str) -> bool:
        """
        Validate if a string is a valid hex color
        
        Args:
            color: Color string to validate
            
        Returns:
            True if valid hex color, False otherwise
        """
        if not color:
            return False
        
        # Remove # if present
        color = color.lstrip("#")
        
        # Check if it's a valid hex color (3, 4, 6, or 8 characters)
        return bool(re.match(r"^[0-9a-fA-F]{3}$|^[0-9a-fA-F]{4}$|^[0-9a-fA-F]{6}$|^[0-9a-fA-F]{8}$", color))

    @staticmethod
    def _check_css_syntax(css: str) -> Tuple[bool, List[str]]:
        """
        Check CSS syntax validity using cssutils
        
        Args:
            css: CSS code to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        try:
            # Parse CSS
            sheet = cssutils.parseString(css)
            
            # Check for parsing errors
            if sheet.cssRules is None:
                errors.append("Failed to parse CSS")
                return False, errors
            
            return True, errors
        except Exception as e:
            errors.append(f"CSS parsing error: {str(e)}")
            return False, errors

    @staticmethod
    def _check_dangerous_properties(css: str) -> List[str]:
        """
        Check for dangerous CSS properties and patterns
        
        Args:
            css: CSS code to check
            
        Returns:
            List of warnings/errors found
        """
        issues = []
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r"@import\s*", "Found @import rule - external resources not allowed"),
            (r"url\s*\(", "Found url() function - external resources not allowed"),
            (r"expression\s*\(", "Found expression() - not allowed"),
            (r"behavior\s*:", "Found behavior property - not allowed"),
            (r"-moz-binding\s*:", "Found -moz-binding - not allowed"),
            (r"-webkit-binding\s*:", "Found -webkit-binding - not allowed"),
            (r"javascript:", "Found javascript: protocol - not allowed"),
            (r"vbscript:", "Found vbscript: protocol - not allowed"),
            (r"<script", "Found script tag - not allowed"),
            (r"onclick\s*=", "Found onclick attribute - not allowed"),
            (r"onerror\s*=", "Found onerror attribute - not allowed"),
            (r"onload\s*=", "Found onload attribute - not allowed"),
        ]
        
        for pattern, message in dangerous_patterns:
            if re.search(pattern, css, re.IGNORECASE):
                issues.append(message)
        
        return issues

    @staticmethod
    def _sanitize_css(css: str) -> str:
        """
        Sanitize CSS by removing dangerous content
        
        Args:
            css: CSS code to sanitize
            
        Returns:
            Sanitized CSS
        """
        # Remove dangerous patterns
        sanitized = css
        
        # Remove @import rules
        sanitized = re.sub(r"@import\s+[^;]*;", "", sanitized, flags=re.IGNORECASE)
        
        # Remove url() functions (but keep data: URIs for gradients)
        sanitized = re.sub(r"url\s*\(\s*(?!data:)[^)]*\)", "none", sanitized, flags=re.IGNORECASE)
        
        # Remove expression()
        sanitized = re.sub(r"expression\s*\([^)]*\)", "", sanitized, flags=re.IGNORECASE)
        
        # Remove javascript: and vbscript: protocols
        sanitized = re.sub(r"(javascript|vbscript):", "", sanitized, flags=re.IGNORECASE)
        
        # Remove script tags
        sanitized = re.sub(r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        sanitized = re.sub(r"on\w+\s*=", "", sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()

    @staticmethod
    def _check_css_size(css: str) -> List[str]:
        """
        Check CSS file size
        
        Args:
            css: CSS code to check
            
        Returns:
            List of warnings if size exceeds limit
        """
        warnings = []
        size = len(css.encode("utf-8"))
        
        if size > ThemeEngineService.MAX_CSS_SIZE:
            warnings.append(
                f"CSS size ({size} bytes) exceeds maximum ({ThemeEngineService.MAX_CSS_SIZE} bytes)"
            )
        
        return warnings

    def validate_custom_css(self, css: str) -> ValidationResult:
        """
        Validate custom CSS for syntax, security, and size
        
        Args:
            css: CSS code to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        if not css:
            return ValidationResult(is_valid=True, sanitized_css="")
        
        # Check size
        size_warnings = self._check_css_size(css)
        warnings.extend(size_warnings)
        
        # Check for dangerous properties
        dangerous_issues = self._check_dangerous_properties(css)
        if dangerous_issues:
            errors.extend(dangerous_issues)
        
        # Check CSS syntax
        is_valid, syntax_errors = self._check_css_syntax(css)
        if not is_valid:
            errors.extend(syntax_errors)
        
        # If there are errors, return invalid
        if errors:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Sanitize CSS
        sanitized = self._sanitize_css(css)
        
        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            sanitized_css=sanitized
        )

    def sanitize_css(self, css: str) -> str:
        """
        Sanitize CSS to remove dangerous content
        
        Args:
            css: CSS code to sanitize
            
        Returns:
            Sanitized CSS
        """
        if not css:
            return ""
        
        # First validate
        result = self.validate_custom_css(css)
        
        if result.sanitized_css:
            return result.sanitized_css
        
        # If validation failed, still try to sanitize
        return self._sanitize_css(css)

    def generate_theme_css(self, branding_config: Dict) -> str:
        """
        Generate CSS variables from branding configuration
        
        Args:
            branding_config: Dictionary with branding settings
            
        Returns:
            CSS string with CSS variables
        """
        css_vars = ":root {\n"
        
        # Color variables
        if branding_config.get("primary_color"):
            css_vars += f"  --primary-color: {branding_config['primary_color']};\n"
        
        if branding_config.get("secondary_color"):
            css_vars += f"  --secondary-color: {branding_config['secondary_color']};\n"
        
        if branding_config.get("accent_color"):
            css_vars += f"  --accent-color: {branding_config['accent_color']};\n"
        
        # Font variables
        if branding_config.get("font_family"):
            css_vars += f"  --font-family: {branding_config['font_family']};\n"
        
        css_vars += "}\n"
        
        return css_vars

    def validate_color_contrast(self, color1: str, color2: str) -> Dict:
        """
        Calculate contrast ratio between two colors (WCAG AA standard: 4.5:1)
        
        Args:
            color1: First color in hex format
            color2: Second color in hex format
            
        Returns:
            Dictionary with contrast ratio and WCAG compliance status
        """
        # Validate colors
        if not self.validate_hex_color(color1) or not self.validate_hex_color(color2):
            return {
                "valid": False,
                "error": "Invalid color format. Use hex colors (e.g., #FF0000)"
            }
        
        # Convert hex to RGB
        def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
            hex_color = hex_color.lstrip("#")
            if len(hex_color) == 3:
                hex_color = "".join([c * 2 for c in hex_color])
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate relative luminance
        def get_luminance(rgb: Tuple[int, int, int]) -> float:
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = get_luminance(rgb1)
        lum2 = get_luminance(rgb2)
        
        # Calculate contrast ratio
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        
        # Check WCAG compliance
        wcag_aa = contrast_ratio >= 4.5
        wcag_aaa = contrast_ratio >= 7.0
        
        return {
            "valid": True,
            "contrast_ratio": round(contrast_ratio, 2),
            "wcag_aa": wcag_aa,
            "wcag_aaa": wcag_aaa,
            "compliant": wcag_aa,
            "message": f"Contrast ratio: {contrast_ratio:.2f}:1 - {'WCAG AA compliant' if wcag_aa else 'Below WCAG AA standard (4.5:1)'}"
        }

    def suggest_accessible_colors(self, base_color: str) -> List[Dict]:
        """
        Suggest accessible color alternatives for a given base color
        
        Args:
            base_color: Base color in hex format
            
        Returns:
            List of suggested colors with contrast ratios
        """
        if not self.validate_hex_color(base_color):
            return []
        
        suggestions = []
        
        # Suggest darker and lighter alternatives
        candidates = [
            "#000000",  # Black
            "#FFFFFF",  # White
            "#333333",  # Dark gray
            "#666666",  # Medium gray
            "#999999",  # Light gray
            "#CCCCCC",  # Very light gray
        ]
        
        for candidate in candidates:
            contrast = self.validate_color_contrast(base_color, candidate)
            if contrast.get("valid"):
                suggestions.append({
                    "color": candidate,
                    "contrast_ratio": contrast["contrast_ratio"],
                    "wcag_aa": contrast["wcag_aa"],
                    "wcag_aaa": contrast["wcag_aaa"]
                })
        
        # Sort by contrast ratio (highest first)
        suggestions.sort(key=lambda x: x["contrast_ratio"], reverse=True)
        
        return suggestions

    def validate_branding_config(self, branding_config: Dict) -> ValidationResult:
        """
        Validate entire branding configuration
        
        Args:
            branding_config: Dictionary with branding settings
            
        Returns:
            ValidationResult with any validation errors
        """
        errors = []
        warnings = []
        
        # Validate colors if present
        if branding_config.get("primary_color"):
            if not self.validate_hex_color(branding_config["primary_color"]):
                errors.append(f"Invalid primary color: {branding_config['primary_color']}")
        
        if branding_config.get("secondary_color"):
            if not self.validate_hex_color(branding_config["secondary_color"]):
                errors.append(f"Invalid secondary color: {branding_config['secondary_color']}")
        
        if branding_config.get("accent_color"):
            if not self.validate_hex_color(branding_config["accent_color"]):
                errors.append(f"Invalid accent color: {branding_config['accent_color']}")
        
        # Check color contrast if both primary and secondary are present
        if (branding_config.get("primary_color") and 
            branding_config.get("secondary_color")):
            contrast = self.validate_color_contrast(
                branding_config["primary_color"],
                branding_config["secondary_color"]
            )
            if contrast.get("valid") and not contrast.get("wcag_aa"):
                warnings.append(
                    f"Color contrast ({contrast['contrast_ratio']}:1) below WCAG AA standard (4.5:1)"
                )
        
        # Validate custom CSS if present
        if branding_config.get("custom_css"):
            css_result = self.validate_custom_css(branding_config["custom_css"])
            if not css_result.is_valid:
                errors.extend(css_result.errors)
            warnings.extend(css_result.warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def inject_css_into_html(self, html: str, css: str, tenant_id: str = None) -> str:
        """
        Inject CSS into HTML head
        
        Args:
            html: HTML content
            css: CSS to inject
            tenant_id: Optional tenant ID for caching purposes
            
        Returns:
            HTML with injected CSS
        """
        if not css or not html:
            return html
        
        # Create style tag with CSS
        style_tag = f'<style id="theme-engine-{tenant_id or "default"}">\n{css}\n</style>'
        
        # Try to inject into head
        if "</head>" in html:
            return html.replace("</head>", f"{style_tag}\n</head>")
        
        # If no head, inject at the beginning
        if "<body>" in html:
            return html.replace("<body>", f"<head>{style_tag}</head>\n<body>")
        
        # Fallback: prepend to HTML
        return style_tag + "\n" + html

    def load_google_font(self, font_family: str) -> str:
        """
        Generate Google Fonts import statement
        
        Args:
            font_family: Font family name (e.g., "Roboto", "Open Sans")
            
        Returns:
            CSS import statement for Google Fonts
        """
        if not font_family:
            return ""
        
        # Sanitize font family name
        font_name = font_family.split(",")[0].strip()
        
        # Replace spaces with + for Google Fonts URL
        font_url_name = font_name.replace(" ", "+")
        
        # Generate import statement
        import_css = f'@import url("https://fonts.googleapis.com/css2?family={font_url_name}:wght@400;500;600;700&display=swap");'
        
        return import_css

    def generate_complete_theme_css(self, branding_config: Dict) -> str:
        """
        Generate complete theme CSS including fonts and variables
        
        Args:
            branding_config: Dictionary with branding settings
            
        Returns:
            Complete CSS string
        """
        css_parts = []
        
        # Add Google Font import if font is specified
        if branding_config.get("font_family"):
            font_import = self.load_google_font(branding_config["font_family"])
            if font_import:
                css_parts.append(font_import)
        
        # Add CSS variables
        css_vars = self.generate_theme_css(branding_config)
        css_parts.append(css_vars)
        
        # Add custom CSS if present and valid
        if branding_config.get("custom_css"):
            validation = self.validate_custom_css(branding_config["custom_css"])
            if validation.is_valid and validation.sanitized_css:
                css_parts.append(validation.sanitized_css)
        
        return "\n".join(css_parts)

    def validate_font_family(self, font_family: str) -> Dict:
        """
        Validate font family name
        
        Args:
            font_family: Font family name to validate
            
        Returns:
            Dictionary with validation result
        """
        if not font_family:
            return {"valid": False, "error": "Font family cannot be empty"}
        
        # Extract primary font name (before comma)
        primary_font = font_family.split(",")[0].strip()
        
        # Check for invalid characters
        invalid_chars = r'[<>"\'{};]'
        if re.search(invalid_chars, primary_font):
            return {
                "valid": False,
                "error": f"Font family contains invalid characters: {primary_font}"
            }
        
        # Check length
        if len(primary_font) > 100:
            return {
                "valid": False,
                "error": "Font family name too long (max 100 characters)"
            }
        
        return {
            "valid": True,
            "font_family": primary_font,
            "message": f"Font family '{primary_font}' is valid"
        }
