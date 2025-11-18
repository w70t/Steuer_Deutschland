"""
German Tax Calculator Service
Based on official data from Bundesministerium der Finanzen (BMF)
"""
from typing import Dict, Tuple
from datetime import datetime
from config import settings
from config.settings import (
    TAX_BRACKETS_2024,
    SOCIAL_SECURITY_2024,
    TAX_CLASSES,
    EMPLOYMENT_TYPES,
    HEALTH_INSURANCE_COMPANIES,
    CHILD_ALLOWANCE,
    GERMAN_STATES
)
import math


class GermanTaxCalculator:
    """Calculate German income tax and social security contributions"""

    def __init__(self, year: int = 2024):
        self.year = year
        self.tax_brackets = TAX_BRACKETS_2024
        self.social_security = SOCIAL_SECURITY_2024

    def calculate_income_tax(
        self,
        annual_income: float,
        tax_class: int,
        kinderfreibetrag: float = 0.0
    ) -> float:
        """
        Calculate income tax based on German tax formula
        Using the official formula from BMF

        Args:
            annual_income: Annual gross income in EUR
            tax_class: Tax class (1-6)
            kinderfreibetrag: Child tax allowance (0.0-6.0)

        Returns:
            Annual income tax in EUR
        """
        # Apply basic allowance (Grundfreibetrag)
        taxable_income = max(0, annual_income - self.tax_brackets['basic_allowance'])

        # Apply Kinderfreibetrag
        if kinderfreibetrag > 0:
            child_deduction = CHILD_ALLOWANCE['per_child'] * kinderfreibetrag
            taxable_income = max(0, taxable_income - child_deduction)

        if taxable_income == 0:
            return 0

        # Round down to full EUR
        zvE = math.floor(taxable_income)

        # Apply German tax formula (Einkommensteuerformel 2024)
        if zvE <= self.tax_brackets['basic_allowance']:
            # Zone 0: No tax
            tax = 0
        elif zvE <= 17005:
            # Zone 1: Progressive from 14% to 24%
            # Formula: (922.98 * y + 1400) * y
            y = (zvE - 11604) / 10000
            tax = (922.98 * y + 1400) * y
        elif zvE <= 66760:
            # Zone 2: Progressive from 24% to 42%
            # Formula: (181.19 * z + 2397) * z + 1025.38
            z = (zvE - 17005) / 10000
            tax = (181.19 * z + 2397) * z + 1025.38
        elif zvE <= 277825:
            # Zone 3: Flat rate 42%
            tax = 0.42 * zvE - 10602.13
        else:
            # Zone 4: Top rate 45% (Reichensteuer)
            tax = 0.45 * zvE - 18936.88

        # Apply tax class adjustments
        tax = self._apply_tax_class_adjustment(tax, tax_class, annual_income)

        return round(tax, 2)

    def _apply_tax_class_adjustment(self, base_tax: float, tax_class: int, income: float) -> float:
        """Apply tax class specific adjustments"""
        if tax_class == 2:
            # Single parent allowance (Entlastungsbetrag für Alleinerziehende)
            relief = 4260  # Base amount for one child
            income -= relief
            # Recalculate with relief
            return max(0, base_tax * 0.95)  # Simplified adjustment
        elif tax_class == 3:
            # Married, higher income - more favorable
            return base_tax * 0.85
        elif tax_class == 5:
            # Married, lower income - less favorable
            return base_tax * 1.15
        elif tax_class == 6:
            # Second job - less favorable, no allowances
            return base_tax * 1.20

        return base_tax

    def calculate_solidarity_surcharge(self, income_tax: float) -> float:
        """
        Calculate solidarity surcharge (Solidaritätszuschlag)
        Only applies if income tax exceeds threshold

        Args:
            income_tax: Annual income tax

        Returns:
            Solidarity surcharge in EUR
        """
        threshold = self.tax_brackets['solidarity_surcharge_threshold']

        if income_tax <= threshold:
            return 0

        rate = self.tax_brackets['solidarity_surcharge_rate'] / 100
        soli = income_tax * rate

        return round(soli, 2)

    def calculate_church_tax(self, income_tax: float, state: str = 'BE_WEST') -> float:
        """
        Calculate church tax (Kirchensteuer)
        8% in Baden-Württemberg and Bavaria, 9% in other states

        Args:
            income_tax: Annual income tax
            state: Federal state code (including BE_WEST, BE_EAST)

        Returns:
            Church tax in EUR
        """
        # Get church tax rate from state
        state_data = GERMAN_STATES.get(state, GERMAN_STATES['BE_WEST'])
        rate = state_data['church_tax']
        church_tax = income_tax * (rate / 100)

        return round(church_tax, 2)

    def calculate_social_security(
        self,
        annual_income: float,
        state: str = 'BE_WEST',
        employment_type: str = 'standard',
        age_group: str = 'under_23',
        health_insurance_company: str = 'tk'
    ) -> Dict[str, float]:
        """
        Calculate social security contributions

        Args:
            annual_income: Annual gross income
            state: Federal state code (determines contribution ceiling)
            employment_type: Type of employment (standard, trainee, civil_servant, self_employed)
            age_group: Age group (under_23, over_23_children, over_23_no_children)
            health_insurance_company: Health insurance company code

        Returns:
            Dictionary with breakdown of contributions
        """
        # Get employment type data
        emp_data = EMPLOYMENT_TYPES.get(employment_type, EMPLOYMENT_TYPES['standard'])

        # For civil servants and self-employed, no social security contributions
        if employment_type in ['civil_servant', 'self_employed']:
            return {
                'health_insurance': 0,
                'pension_insurance': 0,
                'unemployment_insurance': 0,
                'care_insurance': 0,
                'total': 0
            }

        # Get contribution ceiling based on state
        state_data = GERMAN_STATES.get(state, GERMAN_STATES['BE_WEST'])
        ceiling = state_data['contribution_ceiling']

        # Income subject to contributions (capped at ceiling)
        contributable_income = min(annual_income, ceiling)

        # Calculate health insurance based on selected company
        if health_insurance_company != 'private':
            company_data = HEALTH_INSURANCE_COMPANIES.get(
                health_insurance_company,
                HEALTH_INSURANCE_COMPANIES['tk']
            )
            health_rate = company_data['employee_share'] / 100
            health = contributable_income * health_rate
        else:
            # Private insurance - no contribution here, handled separately
            health = 0

        # Calculate pension insurance (employee share only)
        pension_rate = emp_data['pension_rate'] / 2 / 100  # Employee pays half
        pension = contributable_income * pension_rate

        # Calculate unemployment insurance (employee share only)
        unemployment = contributable_income * (self.social_security['unemployment_insurance'] / 2 / 100)

        # Calculate care insurance (Pflegeversicherung)
        care_base_rate = self.social_security['care_insurance'] / 2 / 100

        # Add supplement for 23+ without children (+0.6%)
        if age_group == 'over_23_no_children':
            care_rate = care_base_rate + (0.6 / 100)
        else:
            care_rate = care_base_rate

        care = contributable_income * care_rate

        return {
            'health_insurance': round(health, 2),
            'pension_insurance': round(pension, 2),
            'unemployment_insurance': round(unemployment, 2),
            'care_insurance': round(care, 2),
            'total': round(health + pension + unemployment + care, 2)
        }

    def calculate_net_income(
        self,
        annual_gross: float,
        tax_class: int,
        children: int = 0,
        kinderfreibetrag: float = 0.0,
        church_tax: bool = False,
        state: str = 'BE_WEST',
        employment_type: str = 'standard',
        age_group: str = 'under_23',
        health_insurance_company: str = 'tk'
    ) -> Dict[str, float]:
        """
        Calculate complete net income with all deductions

        Args:
            annual_gross: Annual gross income in EUR
            tax_class: Tax class (1-6)
            children: Number of children (for display purposes)
            kinderfreibetrag: Child tax allowance (0.0-6.0)
            church_tax: Whether church tax applies
            state: Federal state code
            employment_type: Type of employment
            age_group: Age group (affects care insurance)
            health_insurance_company: Health insurance company code

        Returns:
            Dictionary with complete breakdown
        """
        # Calculate income tax
        income_tax = self.calculate_income_tax(annual_gross, tax_class, kinderfreibetrag)

        # Calculate solidarity surcharge
        soli = self.calculate_solidarity_surcharge(income_tax)

        # Calculate church tax if applicable
        church = self.calculate_church_tax(income_tax, state) if church_tax else 0

        # Calculate social security contributions
        social_security = self.calculate_social_security(
            annual_gross,
            state,
            employment_type,
            age_group,
            health_insurance_company
        )

        # Calculate total deductions
        total_tax = income_tax + soli + church
        total_social = social_security['total']
        total_deductions = total_tax + total_social

        # Calculate net income
        net_annual = annual_gross - total_deductions

        return {
            'gross_annual': round(annual_gross, 2),
            'income_tax': round(income_tax, 2),
            'solidarity_surcharge': round(soli, 2),
            'church_tax': round(church, 2),
            'health_insurance': social_security['health_insurance'],
            'pension_insurance': social_security['pension_insurance'],
            'unemployment_insurance': social_security['unemployment_insurance'],
            'care_insurance': social_security['care_insurance'],
            'total_deductions': round(total_deductions, 2),
            'net_annual': round(net_annual, 2),
            'gross_monthly': round(annual_gross / 12, 2),
            'net_monthly': round(net_annual / 12, 2),
            'tax_class': tax_class,
            'children': children,
            'kinderfreibetrag': kinderfreibetrag,
            'employment_type': employment_type,
            'age_group': age_group,
            'health_insurance_company': health_insurance_company,
            'year': self.year
        }


# Global instance
tax_calculator = GermanTaxCalculator()
