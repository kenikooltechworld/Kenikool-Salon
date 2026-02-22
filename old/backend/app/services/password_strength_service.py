"""
Password Strength Service - Password strength calculation and validation
"""
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class PasswordStrengthService:
    """Service for password strength validation and calculation"""

    # Password strength requirements
    MIN_LENGTH = 8
    WEAK_THRESHOLD = 30
    MEDIUM_THRESHOLD = 60
    STRONG_THRESHOLD = 80

    @staticmethod
    def calculate_strength(password: str, username: str = "", email: str = "") -> Dict:
        """
        Calculate password strength
        
        Requirements: 14.1, 14.5, 14.6
        
        Args:
            password: Password to evaluate
            username: Username for similarity check
            email: Email for similarity check
            
        Returns:
            Dict with strength, score, requirements_met, and suggestions
        """
        score = 0
        requirements_met = {}
        suggestions = []
        
        # Check minimum length (Requirement 14.1)
        if len(password) >= PasswordStrengthService.MIN_LENGTH:
            requirements_met["min_length"] = True
            score += 20
        else:
            requirements_met["min_length"] = False
            suggestions.append(f"Password must be at least {PasswordStrengthService.MIN_LENGTH} characters")
        
        # Check for uppercase letters
        if re.search(r'[A-Z]', password):
            requirements_met["uppercase"] = True
            score += 15
        else:
            requirements_met["uppercase"] = False
            suggestions.append("Add uppercase letters (A-Z)")
        
        # Check for lowercase letters
        if re.search(r'[a-z]', password):
            requirements_met["lowercase"] = True
            score += 15
        else:
            requirements_met["lowercase"] = False
            suggestions.append("Add lowercase letters (a-z)")
        
        # Check for numbers
        if re.search(r'\d', password):
            requirements_met["numbers"] = True
            score += 15
        else:
            requirements_met["numbers"] = False
            suggestions.append("Add numbers (0-9)")
        
        # Check for special characters
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
            requirements_met["special_chars"] = True
            score += 15
        else:
            requirements_met["special_chars"] = False
            suggestions.append("Add special characters (!@#$%^&*)")
        
        # Check for common patterns (Requirement 14.5)
        common_patterns = [
            r'123', r'abc', r'qwerty', r'password', r'admin', r'letmein',
            r'welcome', r'monkey', r'dragon', r'master', r'sunshine'
        ]
        
        has_common_pattern = False
        for pattern in common_patterns:
            if re.search(pattern, password, re.IGNORECASE):
                has_common_pattern = True
                break
        
        if has_common_pattern:
            score = max(0, score - 20)
            suggestions.append("Avoid common patterns like '123', 'abc', 'password'")
        
        # Check similarity to username/email (Requirement 14.6)
        if username and PasswordStrengthService._is_similar(password, username):
            score = max(0, score - 15)
            suggestions.append("Password is too similar to your username")
        
        if email:
            email_local = email.split('@')[0]
            if PasswordStrengthService._is_similar(password, email_local):
                score = max(0, score - 15)
                suggestions.append("Password is too similar to your email")
        
        # Determine strength level
        if score >= PasswordStrengthService.STRONG_THRESHOLD:
            strength = "strong"
        elif score >= PasswordStrengthService.MEDIUM_THRESHOLD:
            strength = "medium"
        else:
            strength = "weak"
        
        return {
            "strength": strength,
            "score": min(100, score),
            "requirements_met": requirements_met,
            "suggestions": suggestions
        }

    @staticmethod
    def _is_similar(password: str, text: str, threshold: int = 3) -> bool:
        """
        Check if password is similar to text using Levenshtein distance
        
        Args:
            password: Password to check
            text: Text to compare against
            threshold: Maximum allowed distance
            
        Returns:
            True if similar (distance < threshold)
        """
        password_lower = password.lower()
        text_lower = text.lower()
        
        # Simple substring check
        if text_lower in password_lower or password_lower in text_lower:
            return True
        
        # Levenshtein distance calculation
        distance = PasswordStrengthService._levenshtein_distance(password_lower, text_lower)
        return distance < threshold

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Levenshtein distance
        """
        if len(s1) < len(s2):
            return PasswordStrengthService._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    @staticmethod
    def validate_password(password: str, username: str = "", email: str = "") -> bool:
        """
        Validate if password meets minimum requirements
        
        Args:
            password: Password to validate
            username: Username for similarity check
            email: Email for similarity check
            
        Returns:
            True if password is valid
        """
        result = PasswordStrengthService.calculate_strength(password, username, email)
        return result["strength"] in ["medium", "strong"]

    @staticmethod
    def get_strength_recommendations(password: str, username: str = "", email: str = "") -> List[str]:
        """
        Get recommendations for improving password strength
        
        Args:
            password: Password to evaluate
            username: Username for similarity check
            email: Email for similarity check
            
        Returns:
            List of recommendations
        """
        result = PasswordStrengthService.calculate_strength(password, username, email)
        return result["suggestions"]


# Create singleton instance
password_strength_service = PasswordStrengthService()
