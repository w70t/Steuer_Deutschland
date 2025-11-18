"""
Configuration settings for the German Tax Calculator Bot
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_TELEGRAM_ID = int(os.getenv('ADMIN_TELEGRAM_ID', '0'))

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data/tax_bot.db')

# Tax Update Monitoring
CHECK_UPDATES_INTERVAL_HOURS = int(os.getenv('CHECK_UPDATES_INTERVAL_HOURS', '24'))
TAX_SOURCES_CHECK_ENABLED = os.getenv('TAX_SOURCES_CHECK_ENABLED', 'true').lower() == 'true'

# Official German Tax Sources
BMF_URL = os.getenv('BMF_URL', 'https://www.bundesfinanzministerium.de')
BZST_URL = os.getenv('BZST_URL', 'https://www.bzst.de')
ELSTER_URL = os.getenv('ELSTER_URL', 'https://www.elster.de')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/tax_bot.log')
ERROR_LOG_FILE = os.getenv('ERROR_LOG_FILE', 'logs/errors.log')
ENABLE_DETAILED_ERRORS = os.getenv('ENABLE_DETAILED_ERRORS', 'true').lower() == 'true'
ENABLE_STACK_TRACE = os.getenv('ENABLE_STACK_TRACE', 'true').lower() == 'true'

# Bot Configuration
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'de')
MAX_CALCULATION_HISTORY = int(os.getenv('MAX_CALCULATION_HISTORY', '50'))

# Auto-update Configuration
AUTO_APPLY_UPDATES = os.getenv('AUTO_APPLY_UPDATES', 'false').lower() == 'true'
REQUIRE_ADMIN_APPROVAL = os.getenv('REQUIRE_ADMIN_APPROVAL', 'true').lower() == 'true'

# Supported Languages
SUPPORTED_LANGUAGES: List[str] = [
    'de',  # German
    'ar',  # Arabic
    'tr',  # Turkish
    'pl',  # Polish
    'ru',  # Russian
    'it',  # Italian
    'ro',  # Romanian
    'en',  # English
    'el',  # Greek
    'hr',  # Croatian
]

# Tax Brackets 2024 (will be updated automatically)
TAX_BRACKETS_2024 = {
    'basic_allowance': 11604,  # Grundfreibetrag
    'brackets': [
        {'from': 0, 'to': 11604, 'rate': 0},
        {'from': 11605, 'to': 17005, 'rate': 'progressive'},  # 14% to 24%
        {'from': 17006, 'to': 66760, 'rate': 'progressive'},  # 24% to 42%
        {'from': 66761, 'to': 277825, 'rate': 42},
        {'from': 277826, 'to': float('inf'), 'rate': 45},  # Reichensteuer
    ],
    'solidarity_surcharge_threshold': 18130,  # Solidaritätszuschlag
    'solidarity_surcharge_rate': 5.5,
    'church_tax_rate': 8,  # or 9% depending on state
}

# Social Security Contributions 2024
SOCIAL_SECURITY_2024 = {
    'health_insurance': 14.6,  # Krankenversicherung (employee: 7.3%)
    'pension_insurance': 18.6,  # Rentenversicherung (employee: 9.3%)
    'unemployment_insurance': 2.6,  # Arbeitslosenversicherung (employee: 1.3%)
    'care_insurance': 3.4,  # Pflegeversicherung (employee: 1.7%)
    'contribution_ceiling': 62100,  # BBG West
    'contribution_ceiling_east': 58800,  # BBG East
}

# Tax Classes (Steuerklassen)
TAX_CLASSES = {
    1: 'Single, divorced, widowed',
    2: 'Single parent',
    3: 'Married, higher income',
    4: 'Married, similar income',
    5: 'Married, lower income',
    6: 'Second job',
}

# German States (Bundesländer) with church tax rates
GERMAN_STATES = {
    'BW': {'name': 'Baden-Württemberg', 'church_tax': 8},
    'BY': {'name': 'Bayern', 'church_tax': 8},
    'BE': {'name': 'Berlin', 'church_tax': 9},
    'BB': {'name': 'Brandenburg', 'church_tax': 9},
    'HB': {'name': 'Bremen', 'church_tax': 9},
    'HH': {'name': 'Hamburg', 'church_tax': 9},
    'HE': {'name': 'Hessen', 'church_tax': 9},
    'MV': {'name': 'Mecklenburg-Vorpommern', 'church_tax': 9},
    'NI': {'name': 'Niedersachsen', 'church_tax': 9},
    'NW': {'name': 'Nordrhein-Westfalen', 'church_tax': 9},
    'RP': {'name': 'Rheinland-Pfalz', 'church_tax': 9},
    'SL': {'name': 'Saarland', 'church_tax': 9},
    'SN': {'name': 'Sachsen', 'church_tax': 9},
    'ST': {'name': 'Sachsen-Anhalt', 'church_tax': 9},
    'SH': {'name': 'Schleswig-Holstein', 'church_tax': 9},
    'TH': {'name': 'Thüringen', 'church_tax': 9},
}

# Calculation period options
CALCULATION_PERIODS = {
    'monthly': 'Monthly',
    'annual': 'Annual'
}

def validate_config():
    """Validate required configuration"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    if not ADMIN_TELEGRAM_ID:
        raise ValueError("ADMIN_TELEGRAM_ID is required")

    # Create necessary directories
    (BASE_DIR / 'data').mkdir(exist_ok=True)
    (BASE_DIR / 'logs').mkdir(exist_ok=True)

    return True
