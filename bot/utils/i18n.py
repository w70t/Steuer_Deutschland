"""Internationalization (i18n) utilities for multi-language support"""
import json
from pathlib import Path
from typing import Dict, Optional
from config import BASE_DIR, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


class I18nManager:
    """Manage translations for multiple languages"""

    def __init__(self):
        self.locales_path = BASE_DIR / 'bot' / 'locales'
        self.translations: Dict[str, Dict[str, str]] = {}
        self.load_all_translations()

    def load_all_translations(self):
        """Load all translation files"""
        for lang_code in SUPPORTED_LANGUAGES:
            self.load_language(lang_code)

    def load_language(self, lang_code: str):
        """Load translations for a specific language"""
        lang_file = self.locales_path / lang_code / 'messages.json'
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Translation file for {lang_code} not found")
            self.translations[lang_code] = {}

    def get(self, key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
        """
        Get translated message for a key

        Args:
            key: Translation key
            lang: Language code (default: German)
            **kwargs: Format arguments for string formatting

        Returns:
            Translated message with format args applied
        """
        # Fallback to default language if requested language not found
        if lang not in self.translations:
            lang = DEFAULT_LANGUAGE

        # Get translation or return key if not found
        message = self.translations.get(lang, {}).get(key, key)

        # Apply formatting if kwargs provided
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Missing format key {e} in translation '{key}'")

        return message

    def get_language_name(self, lang_code: str) -> str:
        """Get the native name of a language"""
        language_names = {
            'de': '🇩🇪 Deutsch',
            'ar': '🇸🇦 العربية',
            'tr': '🇹🇷 Türkçe',
            'pl': '🇵🇱 Polski',
            'ru': '🇷🇺 Русский',
            'it': '🇮🇹 Italiano',
            'ro': '🇷🇴 Română',
            'en': '🇬🇧 English',
            'el': '🇬🇷 Ελληνικά',
            'hr': '🇭🇷 Hrvatski',
        }
        return language_names.get(lang_code, lang_code)

    def is_supported(self, lang_code: str) -> bool:
        """Check if a language is supported"""
        return lang_code in SUPPORTED_LANGUAGES


# Global instance
i18n = I18nManager()


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs) -> str:
    """
    Shorthand function for getting translations

    Usage:
        t('welcome', lang='en')
        t('calculation_result', lang='de', gross=50000, net=35000)
    """
    return i18n.get(key, lang, **kwargs)
