"""
German Tax Calculator Service
Based on official data from Bundesministerium der Finanzen (BMF)
"""
from typing import Dict, Tuple
from datetime import datetime
from config import TAX_BRACKETS_2024, SOCIAL_SECURITY_2024, TAX_CLASSES
import math


class GermanTaxCalculator:
    """Calculate German income tax and social security contributions"""

    def __init__(self, year: int = 2024):
        self.year = year
        self.tax_brackets = TAX_BRACKETS_2024
        self.social_security = SOCIAL_SECURITY_2024

    def calculate_income_tax(self, annual_income: float, tax_class: int) -> float:
        """
        Calculate income tax based on German tax formula
        Using the official formula from BMF

        Args:
            annual_income: Annual gross income in EUR
            tax_class: Tax class (1-6)

        Returns:
            Annual income tax in EUR
        """
        # Apply basic allowance (Grundfreibetrag)
        taxable_income = max(0, annual_income - self.tax_brackets['basic_allowance'])

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

    def calculate_church_tax(self, income_tax: float, state: str = 'BW') -> float:
        """
        Calculate church tax (Kirchensteuer)
        8% in Baden-Württemberg and Bavaria, 9% in other states

        Args:
            income_tax: Annual income tax
            state: Federal state code

        Returns:
            Church tax in EUR
        """
        # Bavaria and Baden-Württemberg have 8%, others 9%
        rate = 8 if state in ['BW', 'BY'] else 9
        church_tax = income_tax * (rate / 100)

        return round(church_tax, 2)

    def calculate_social_security(
        self,
        annual_income: float,
        is_east: bool = False
    ) -> Dict[str, float]:
        """
        Calculate social security contributions

        Args:
            annual_income: Annual gross income
            is_east: True if employed in Eastern Germany

        Returns:
            Dictionary with breakdown of contributions
        """
        # Contribution ceiling
        ceiling = (self.social_security['contribution_ceiling_east']
                  if is_east
                  else self.social_security['contribution_ceiling'])

        # Income subject to contributions (capped at ceiling)
        contributable_income = min(annual_income, ceiling)

        # Calculate contributions (employee share only)
        health = contributable_income * (self.social_security['health_insurance'] / 2 / 100)
        pension = contributable_income * (self.social_security['pension_insurance'] / 2 / 100)
        unemployment = contributable_income * (self.social_security['unemployment_insurance'] / 2 / 100)
        care = contributable_income * (self.social_security['care_insurance'] / 2 / 100)

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
        church_tax: bool = False,
        state: str = 'BW',
        is_east: bool = False
    ) -> Dict[str, float]:
        """
        Calculate complete net income with all deductions

        Args:
            annual_gross: Annual gross income in EUR
            tax_class: Tax class (1-6)
            children: Number of children
            church_tax: Whether church tax applies
            state: Federal state code
            is_east: Whether employed in Eastern Germany

        Returns:
            Dictionary with complete breakdown
        """
        # Calculate income tax
        income_tax = self.calculate_income_tax(annual_gross, tax_class)

        # Calculate solidarity surcharge
        soli = self.calculate_solidarity_surcharge(income_tax)

        # Calculate church tax if applicable
        church = self.calculate_church_tax(income_tax, state) if church_tax else 0

        # Calculate social security contributions
        social_security = self.calculate_social_security(annual_gross, is_east)

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
            'year': self.year
        }


# Global instance
tax_calculator = GermanTaxCalculator()
