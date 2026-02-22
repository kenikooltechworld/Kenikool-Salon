"""
Accessibility Service - Ensure WCAG 2.1 AA compliance
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class AccessibilityService:
    """Service for accessibility compliance"""
    
    @staticmethod
    def get_wcag_guidelines() -> Dict:
        """Get WCAG 2.1 AA compliance guidelines"""
        return {
            "perceivable": {
                "text_alternatives": "Provide text alternatives for all non-text content",
                "adaptable": "Make content adaptable and distinguishable",
                "color_contrast": "Minimum 4.5:1 for normal text, 3:1 for large text",
                "readable": "Make text readable and understandable"
            },
            "operable": {
                "keyboard_accessible": "All functionality available from keyboard",
                "enough_time": "Provide users enough time to read and use content",
                "seizures": "Do not design content that causes seizures",
                "navigable": "Provide ways to help users navigate and find content"
            },
            "understandable": {
                "readable": "Make text readable and understandable",
                "predictable": "Make web pages appear and operate in predictable ways",
                "input_assistance": "Help users avoid and correct mistakes"
            },
            "robust": {
                "compatible": "Maximize compatibility with current and future assistive technologies"
            }
        }
    
    @staticmethod
    def get_color_contrast_requirements() -> Dict:
        """Get color contrast requirements"""
        return {
            "normal_text": {
                "minimum": 4.5,
                "enhanced": 7
            },
            "large_text": {
                "minimum": 3,
                "enhanced": 4.5
            },
            "ui_components": {
                "minimum": 3
            }
        }
    
    @staticmethod
    def get_keyboard_navigation_guidelines() -> List[str]:
        """Get keyboard navigation guidelines"""
        return [
            "All interactive elements must be keyboard accessible",
            "Tab order must be logical and intuitive",
            "Focus indicator must be visible",
            "Keyboard shortcuts should be available",
            "No keyboard trap - users can navigate away from any element",
            "Escape key should close modals and dropdowns",
            "Enter/Space should activate buttons",
            "Arrow keys should navigate lists and menus"
        ]
    
    @staticmethod
    def get_screen_reader_guidelines() -> List[str]:
        """Get screen reader guidelines"""
        return [
            "Use semantic HTML elements",
            "Provide ARIA labels for all interactive elements",
            "Associate labels with form inputs",
            "Use ARIA roles for custom components",
            "Announce dynamic content changes",
            "Provide skip links for navigation",
            "Use heading hierarchy correctly",
            "Describe images with alt text",
            "Use ARIA live regions for updates"
        ]
    
    @staticmethod
    def get_mobile_accessibility_guidelines() -> List[str]:
        """Get mobile accessibility guidelines"""
        return [
            "Touch targets minimum 44x44 pixels",
            "Avoid small text (minimum 12px)",
            "Provide sufficient spacing between interactive elements",
            "Support both portrait and landscape orientations",
            "Avoid horizontal scrolling",
            "Use readable fonts",
            "Provide clear visual feedback for interactions",
            "Support system text size preferences",
            "Avoid auto-playing audio/video",
            "Provide captions for video content"
        ]
    
    @staticmethod
    def get_form_accessibility_guidelines() -> List[str]:
        """Get form accessibility guidelines"""
        return [
            "Label all form fields",
            "Group related fields with fieldset",
            "Provide clear error messages",
            "Indicate required fields",
            "Provide input hints and examples",
            "Use appropriate input types",
            "Validate on blur, not on keystroke",
            "Allow form submission with Enter key",
            "Provide success confirmation",
            "Allow users to review before submitting"
        ]
    
    @staticmethod
    def get_focus_management_guidelines() -> List[str]:
        """Get focus management guidelines"""
        return [
            "Focus should be visible at all times",
            "Focus indicator should have sufficient contrast",
            "Focus order should be logical",
            "Focus should not be trapped",
            "Modal dialogs should trap focus",
            "Focus should return to trigger element when modal closes",
            "Skip links should be available",
            "Focus should be managed for dynamic content"
        ]
    
    @staticmethod
    def get_testing_checklist() -> Dict:
        """Get accessibility testing checklist"""
        return {
            "keyboard_navigation": [
                "Tab through all interactive elements",
                "Verify logical tab order",
                "Check for keyboard traps",
                "Test with screen reader"
            ],
            "visual_design": [
                "Check color contrast ratios",
                "Verify focus indicators are visible",
                "Check text size and readability",
                "Verify color is not the only indicator"
            ],
            "content": [
                "Verify all images have alt text",
                "Check heading hierarchy",
                "Verify form labels are present",
                "Check for sufficient spacing"
            ],
            "mobile": [
                "Test on mobile devices",
                "Verify touch targets are 44x44px",
                "Check landscape orientation",
                "Test with mobile screen reader"
            ],
            "tools": [
                "Use WAVE browser extension",
                "Use Axe DevTools",
                "Use Lighthouse",
                "Use NVDA or JAWS screen reader",
                "Use keyboard only navigation"
            ]
        }


# Singleton instance
accessibility_service = AccessibilityService()
