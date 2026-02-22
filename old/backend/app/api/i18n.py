"""
Internationalization and Localization API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import json
from pathlib import Path

from app.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/i18n", tags=["i18n"])

# ===== REQUEST/RESPONSE SCHEMAS =====

class LanguagePreferenceRequest(BaseModel):
    """Language preference update request"""
    language: str = Field(..., min_length=2, max_length=5)


class LanguagePreferenceResponse(BaseModel):
    """Language preference response"""
    language: str
    user_id: str


class SupportedLanguage(BaseModel):
    """Supported language info"""
    code: str
    name: str
    native_name: str
    direction: str  # 'ltr' or 'rtl'


class LocaleFormatting(BaseModel):
    """Locale-specific formatting rules"""
    language: str
    date_format: str
    currency: str
    currency_symbol: str
    decimal_separator: str
    thousands_separator: str
    number_format: str


# ===== CONSTANTS =====

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "native_name": "English",
        "direction": "ltr"
    },
    "es": {
        "name": "Spanish",
        "native_name": "Español",
        "direction": "ltr"
    },
    "fr": {
        "name": "French",
        "native_name": "Français",
        "direction": "ltr"
    },
    "ar": {
        "name": "Arabic",
        "native_name": "العربية",
        "direction": "rtl"
    }
}

LOCALE_FORMATTING = {
    "en": {
        "date_format": "MM/DD/YYYY",
        "currency": "USD",
        "currency_symbol": "$",
        "decimal_separator": ".",
        "thousands_separator": ",",
        "number_format": "#,##0.##"
    },
    "es": {
        "date_format": "DD/MM/YYYY",
        "currency": "USD",
        "currency_symbol": "$",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "number_format": "#.##0,##"
    },
    "fr": {
        "date_format": "DD/MM/YYYY",
        "currency": "EUR",
        "currency_symbol": "€",
        "decimal_separator": ",",
        "thousands_separator": " ",
        "number_format": "# ##0,##"
    },
    "ar": {
        "date_format": "DD/MM/YYYY",
        "currency": "SAR",
        "currency_symbol": "﷼",
        "decimal_separator": ",",
        "thousands_separator": ".",
        "number_format": "#,##0.##"
    }
}

NAMESPACES = [
    "common",
    "booking",
    "clients",
    "staff",
    "services",
    "inventory",
    "payments",
    "marketing",
    "giftcards",
    "reviews",
    "settings",
    "errors"
]


# ===== HELPER FUNCTIONS =====

def get_translations_path() -> Path:
    """Get the path to translation files"""
    # Assuming translations are in kenzola/src/locales
    # For backend, we'll serve them from a backend directory or return metadata
    return Path(__file__).parent.parent.parent.parent / "kenzola" / "src" / "locales"


def load_translation_file(language: str, namespace: str) -> Dict[str, Any]:
    """Load a translation file"""
    try:
        translations_path = get_translations_path()
        file_path = translations_path / language / f"{namespace}.json"
        
        if not file_path.exists():
            logger.warning(f"Translation file not found: {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading translation file {language}/{namespace}: {e}")
        return {}


# ===== ENDPOINTS =====

@router.get("/languages", response_model=list[SupportedLanguage])
async def get_supported_languages():
    """
    Get list of supported languages
    
    Returns:
        List of supported languages with metadata
    """
    try:
        languages = []
        for code, info in SUPPORTED_LANGUAGES.items():
            languages.append(SupportedLanguage(
                code=code,
                name=info["name"],
                native_name=info["native_name"],
                direction=info["direction"]
            ))
        return languages
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get supported languages"
        )


@router.get("/translations/{language}/{namespace}")
async def get_translations(language: str, namespace: str):
    """
    Get translations for a specific language and namespace
    
    Args:
        language: Language code (e.g., 'en', 'es', 'fr', 'ar')
        namespace: Namespace (e.g., 'common', 'booking', 'clients')
    
    Returns:
        Translation dictionary for the specified language and namespace
    """
    try:
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {language}"
            )
        
        # Validate namespace
        if namespace not in NAMESPACES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid namespace: {namespace}"
            )
        
        # Load translations
        translations = load_translation_file(language, namespace)
        
        return {
            "language": language,
            "namespace": namespace,
            "translations": translations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting translations for {language}/{namespace}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get translations"
        )


@router.get("/locales/{language}", response_model=LocaleFormatting)
async def get_locale_formatting(language: str):
    """
    Get locale-specific formatting rules
    
    Args:
        language: Language code (e.g., 'en', 'es', 'fr', 'ar')
    
    Returns:
        Locale-specific formatting rules
    """
    try:
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {language}"
            )
        
        formatting = LOCALE_FORMATTING.get(language, LOCALE_FORMATTING["en"])
        
        return LocaleFormatting(
            language=language,
            **formatting
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting locale formatting for {language}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get locale formatting"
        )


@router.get("/users/preferences/language")
async def get_user_language_preference(current_user: Dict = Depends(get_current_user)):
    """
    Get current user's language preference
    
    Returns:
        User's language preference
    """
    try:
        # Get language preference from user dict
        language = current_user.get('language_preference', 'en')
        
        return {
            "user_id": current_user.get('user_id'),
            "language": language
        }
    except Exception as e:
        logger.error(f"Error getting user language preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get language preference"
        )


@router.post("/users/preferences/language", response_model=LanguagePreferenceResponse)
async def set_user_language_preference(
    request: LanguagePreferenceRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Set current user's language preference
    
    Args:
        request: Language preference update request
        current_user: Current authenticated user
    
    Returns:
        Updated language preference
    """
    try:
        # Validate language
        if request.language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {request.language}"
            )
        
        # Note: Language preference update would require database access
        # For now, we'll just return the preference without persisting
        logger.info(f"User {current_user.get('user_id')} language preference set to {request.language}")
        
        return LanguagePreferenceResponse(
            language=request.language,
            user_id=current_user.get('user_id')
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting user language preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set language preference"
        )


@router.get("/namespaces")
async def get_namespaces():
    """
    Get list of available translation namespaces
    
    Returns:
        List of namespace names
    """
    try:
        return {
            "namespaces": NAMESPACES
        }
    except Exception as e:
        logger.error(f"Error getting namespaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get namespaces"
        )


@router.get("/all-translations/{language}")
async def get_all_translations(language: str):
    """
    Get all translations for a specific language (all namespaces)
    
    Args:
        language: Language code (e.g., 'en', 'es', 'fr', 'ar')
    
    Returns:
        Dictionary with all translations organized by namespace
    """
    try:
        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported language: {language}"
            )
        
        all_translations = {}
        
        # Load all namespaces for this language
        for namespace in NAMESPACES:
            translations = load_translation_file(language, namespace)
            all_translations[namespace] = translations
        
        return {
            "language": language,
            "translations": all_translations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting all translations for {language}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get all translations"
        )
