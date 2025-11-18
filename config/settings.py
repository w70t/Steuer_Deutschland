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

# Tax Classes (Steuerklassen) with detailed descriptions
TAX_CLASSES = {
    1: {
        'code': 1,
        'name_de': 'Ledige und Allein-Lebende ohne Kinder',
        'name_en': 'Single without children',
        'description_de': 'Für unverheiratete, geschiedene oder verwitwete Arbeitnehmer ohne Kinder',
        'description_ar': 'للعمال غير المتزوجين أو المطلقين أو الأرامل بدون أطفال'
    },
    2: {
        'code': 2,
        'name_de': 'Ledige und Allein-Lebende mit Kindern',
        'name_en': 'Single parent with children',
        'description_de': 'Für Alleinerziehende mit Kindern (Entlastungsbetrag)',
        'description_ar': 'للآباء الوحيدين مع أطفال (إعفاء ضريبي)'
    },
    3: {
        'code': 3,
        'name_de': 'Verheirateter Alleinverdiener',
        'name_en': 'Married, sole earner (higher income)',
        'description_de': 'Für verheiratete Alleinverdiener oder höheres Einkommen',
        'description_ar': 'للمتزوجين المعيل الوحيد أو الدخل الأعلى'
    },
    4: {
        'code': 4,
        'name_de': 'Verheirateter Doppelverdiener',
        'name_en': 'Married, both working (equal income)',
        'description_de': 'Für verheiratete Doppelverdiener mit ähnlichem Einkommen',
        'description_ar': 'للمتزوجين كلاهما يعمل بدخل متساوي'
    },
    5: {
        'code': 5,
        'name_de': 'Verheirateter Doppelverdiener mit geringerem Einkommen',
        'name_en': 'Married, both working (lower income)',
        'description_de': 'Für den Partner mit geringerem Einkommen (Partner hat Steuerklasse 3)',
        'description_ar': 'للشريك ذو الدخل الأقل (الشريك لديه فئة 3)'
    },
    6: {
        'code': 6,
        'name_de': 'Nebenverdienst eines Arbeitnehmers',
        'name_en': 'Second job / additional income',
        'description_de': 'Für zweites Arbeitsverhältnis oder Nebenjob',
        'description_ar': 'للوظيفة الثانية أو العمل الإضافي'
    },
}

# Employment Types (Beschäftigungsart)
EMPLOYMENT_TYPES = {
    'standard': {
        'name_de': 'Standard, Angestellte',
        'name_en': 'Standard employee',
        'description_de': 'Regulär angestellte Arbeitnehmer',
        'description_ar': 'موظف عادي',
        'pension_rate': 18.6,  # Normal pension insurance rate
    },
    'trainee': {
        'name_de': 'Azubi',
        'name_en': 'Trainee/Apprentice',
        'description_de': 'Auszubildende',
        'description_ar': 'متدرب/متمرن',
        'pension_rate': 18.6,
        'special_rules': True,
    },
    'civil_servant': {
        'name_de': 'Beamte, Soldaten',
        'name_en': 'Civil servant, soldier',
        'description_de': 'Beamte und Soldaten (keine Sozialversicherung)',
        'description_ar': 'موظف حكومي/جندي (بدون تأمينات اجتماعية)',
        'pension_rate': 0,  # No social security
        'health_insurance': 'private',  # Usually private
    },
    'self_employed': {
        'name_de': 'Sonstige, Selbständige',
        'name_en': 'Self-employed, freelancer',
        'description_de': 'Selbständige und Freiberufler',
        'description_ar': 'عامل حر/مستقل',
        'pension_rate': 0,  # Optional
        'health_insurance': 'voluntary',
    },
}

# German States (Bundesländer) with church tax rates and East/West distinction
# East Germany has different pension contribution ceilings
GERMAN_STATES = {
    'BW': {
        'name': 'Baden-Württemberg',
        'church_tax': 8,
        'is_east': False,
        'contribution_ceiling': 62100  # BBG West 2024
    },
    'BY': {
        'name': 'Bayern',
        'church_tax': 8,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'BE_WEST': {
        'name': 'Berlin (West)',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'BE_EAST': {
        'name': 'Berlin (Ost)',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800  # BBG East 2024
    },
    'BB': {
        'name': 'Brandenburg',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800
    },
    'HB': {
        'name': 'Bremen',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'HH': {
        'name': 'Hamburg',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'HE': {
        'name': 'Hessen',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'MV': {
        'name': 'Mecklenburg-Vorpommern',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800
    },
    'NI': {
        'name': 'Niedersachsen',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'NW': {
        'name': 'Nordrhein-Westfalen',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'RP': {
        'name': 'Rheinland-Pfalz',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'SL': {
        'name': 'Saarland',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'SN': {
        'name': 'Sachsen',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800
    },
    'ST': {
        'name': 'Sachsen-Anhalt',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800
    },
    'SH': {
        'name': 'Schleswig-Holstein',
        'church_tax': 9,
        'is_east': False,
        'contribution_ceiling': 62100
    },
    'TH': {
        'name': 'Thüringen',
        'church_tax': 9,
        'is_east': True,
        'contribution_ceiling': 58800
    },
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
    'viactiv': {
        'name': 'VIACTIV Krankenkasse',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'pronova': {
        'name': 'pronova BKK',
        'base_rate': 14.6,
        'additional_rate': 1.69,
        'total_rate': 16.29,
        'employee_share': 8.95,
    },
    'sbk': {
        'name': 'Siemens-Betriebskrankenkasse (SBK)',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'big_direkt': {
        'name': 'BIG direkt gesund',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'aok_rheinland': {
        'name': 'AOK Rheinland/Hamburg',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'aok_nordwest': {
        'name': 'AOK NordWest',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'aok_hessen': {
        'name': 'AOK Hessen',
        'base_rate': 14.6,
        'additional_rate': 1.9,
        'total_rate': 16.5,
        'employee_share': 9.15,
    },
    'salus': {
        'name': 'Salus BKK',
        'base_rate': 14.6,
        'additional_rate': 1.49,
        'total_rate': 16.09,
        'employee_share': 8.79,
    },
    'energie_bkk': {
        'name': 'Energie-BKK',
        'base_rate': 14.6,
        'additional_rate': 1.7,
        'total_rate': 16.3,
        'employee_share': 8.95,
    },
}

# Age groups for care insurance (Pflegeversicherung)
# People over 23 without children pay additional 0.6%
AGE_GROUPS = {
    'under_23': {'name': 'Under 23 years', 'care_supplement': 0},
    'over_23_with_children': {'name': '23+ years with children', 'care_supplement': 0},
    'over_23_no_children': {'name': '23+ years without children', 'care_supplement': 0.6},
}

# Child allowance (Kinderfreibetrag) - Tax allowance per child
# Values for 2024: €6,384 per child (both parents together)
CHILD_ALLOWANCE = {
    'per_child': 6384,  # Total for both parents
    'single_parent': 3192,  # Half for single parent
    'education_allowance': 2928,  # Freibetrag für Betreuung und Erziehung
}

# Kinderfreibetrag options (0.0 - 6.0 in 0.5 steps)
KINDERFREIBETRAG_OPTIONS = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]

# Private Health Insurance options
PRIVATE_HEALTH_INSURANCE = {
    'employer_subsidy_max': 421.76,  # Maximum employer contribution 2024 (50% of max GKV)
    'description_de': 'Private Krankenversicherung',
    'description_ar': 'تأمين صحي خاص',
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
