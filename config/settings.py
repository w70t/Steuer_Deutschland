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

# Tax Update Monitoring - Check every 10 minutes for updates
CHECK_UPDATES_INTERVAL_MINUTES = int(os.getenv('CHECK_UPDATES_INTERVAL_MINUTES', '10'))
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

# German Health Insurance Companies (Krankenkassen) with rates 2024
# Base rate (Grundbeitrag): 14.6% (split 50/50 between employer and employee)
# Additional contribution (Zusatzbeitrag): varies by insurance, paid by employee only
HEALTH_INSURANCE_COMPANIES = {
    'aok_bw': {
        'name': 'AOK Baden-Württemberg',
        'base_rate': 14.6,
        'additional_rate': 1.7,
        'total_rate': 16.3,
        'employee_share': 8.95,  # 7.3% + 1.7% additional
    },
    'aok_bayern': {
        'name': 'AOK Bayern',
        'base_rate': 14.6,
        'additional_rate': 1.7,
        'total_rate': 16.3,
        'employee_share': 8.95,
    },
    'aok_nds': {
        'name': 'AOK Niedersachsen',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,  # 7.3% + 1.9% additional
    },
    'aok_plus': {
        'name': 'AOK PLUS (Sachsen/Thüringen)',
        'base_rate': 14.6,
        'additional_rate': 1.38,
        'total_rate': 15.98,
        'employee_share': 8.68,
    },
    'tk': {
        'name': 'Techniker Krankenkasse (TK)',
        'base_rate': 14.6,
        'additional_rate': 1.2,
        'total_rate': 15.8,
        'employee_share': 8.5,  # 7.3% + 1.2% additional
    },
    'barmer': {
        'name': 'Barmer',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'dak': {
        'name': 'DAK-Gesundheit',
        'base_rate': 14.6,
        'additional_rate': 1.7,
        'total_rate': 16.3,
        'employee_share': 8.95,
    },
    'hkk': {
        'name': 'hkk Krankenkasse',
        'base_rate': 14.6,
        'additional_rate': 1.19,
        'total_rate': 15.79,
        'employee_share': 8.49,  # Lowest rate!
    },
    'ikk_classic': {
        'name': 'IKK classic',
        'base_rate': 14.6,
        'additional_rate': 1.5,
        'total_rate': 16.1,
        'employee_share': 8.8,
    },
    'bkk24': {
        'name': 'BKK24',
        'base_rate': 14.6,
        'additional_rate': 1.79,
        'total_rate': 16.39,
        'employee_share': 9.09,
    },
    'bkk_vbu': {
        'name': 'BKK VBU',
        'base_rate': 14.6,
        'additional_rate': 1.6,
        'total_rate': 16.2,
        'employee_share': 8.9,
    },
    'knappschaft': {
        'name': 'Knappschaft',
        'base_rate': 14.6,
        'additional_rate': 1.7,
        'total_rate': 16.3,
        'employee_share': 8.95,
    },
    'debeka': {
        'name': 'Debeka BKK',
        'base_rate': 14.6,
        'additional_rate': 1.49,
        'total_rate': 16.09,
        'employee_share': 8.79,
    },
}

# Age groups for care insurance (Pflegeversicherung)
# People over 23 without children pay additional 0.6%
AGE_GROUPS = {
    'under_23': {'name': 'Under 23 years', 'care_supplement': 0},
    'over_23_with_children': {'name': '23+ years with children', 'care_supplement': 0},
    'over_23_no_children': {'name': '23+ years without children', 'care_supplement': 0.6},
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
