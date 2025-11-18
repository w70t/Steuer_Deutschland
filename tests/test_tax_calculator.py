"""
Tests for German Tax Calculator
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.services.tax_calculator import GermanTaxCalculator


def test_tax_calculator_initialization():
    """Test calculator initialization"""
    calculator = GermanTaxCalculator(year=2024)
    assert calculator.year == 2024


def test_basic_allowance():
    """Test that income below basic allowance pays no tax"""
    calculator = GermanTaxCalculator()

    # Income below basic allowance (11,604 EUR)
    result = calculator.calculate_net_income(
        annual_gross=10000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Should have no income tax
    assert result['income_tax'] == 0
    assert result['solidarity_surcharge'] == 0


def test_middle_income_class_1():
    """Test middle income calculation for class 1"""
    calculator = GermanTaxCalculator()

    result = calculator.calculate_net_income(
        annual_gross=45000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Should have income tax
    assert result['income_tax'] > 0

    # Should have social security contributions
    assert result['health_insurance'] > 0
    assert result['pension_insurance'] > 0
    assert result['unemployment_insurance'] > 0
    assert result['care_insurance'] > 0

    # Net should be less than gross
    assert result['net_annual'] < result['gross_annual']

    # Net should be positive
    assert result['net_annual'] > 0


def test_high_income():
    """Test high income calculation"""
    calculator = GermanTaxCalculator()

    result = calculator.calculate_net_income(
        annual_gross=100000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Should have significant income tax
    assert result['income_tax'] > 20000

    # Should have solidarity surcharge
    assert result['solidarity_surcharge'] > 0


def test_church_tax():
    """Test church tax calculation"""
    calculator = GermanTaxCalculator()

    result_with_church = calculator.calculate_net_income(
        annual_gross=50000,
        tax_class=1,
        children=0,
        church_tax=True
    )

    result_without_church = calculator.calculate_net_income(
        annual_gross=50000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # With church tax should have church tax amount
    assert result_with_church['church_tax'] > 0

    # Without church tax should have no church tax
    assert result_without_church['church_tax'] == 0

    # Net income should be lower with church tax
    assert result_with_church['net_annual'] < result_without_church['net_annual']


def test_different_tax_classes():
    """Test different tax classes"""
    calculator = GermanTaxCalculator()

    results = {}
    for tax_class in [1, 2, 3, 4, 5, 6]:
        result = calculator.calculate_net_income(
            annual_gross=50000,
            tax_class=tax_class,
            children=0,
            church_tax=False
        )
        results[tax_class] = result

    # All should have income tax
    for tax_class, result in results.items():
        assert result['income_tax'] > 0, f"Tax class {tax_class} should have income tax"


def test_social_security_ceiling():
    """Test that social security contributions are capped"""
    calculator = GermanTaxCalculator()

    # Very high income
    result = calculator.calculate_net_income(
        annual_gross=200000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Social security should be capped
    # Health insurance employee share should not exceed ~4,500 EUR annually
    assert result['health_insurance'] < 5000


def test_monthly_calculation():
    """Test that monthly values are calculated correctly"""
    calculator = GermanTaxCalculator()

    result = calculator.calculate_net_income(
        annual_gross=48000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Monthly gross should be annual / 12
    assert result['gross_monthly'] == result['gross_annual'] / 12

    # Monthly net should be annual / 12
    assert result['net_monthly'] == result['net_annual'] / 12


def test_progressive_tax():
    """Test that higher income pays higher percentage"""
    calculator = GermanTaxCalculator()

    low_income = calculator.calculate_net_income(
        annual_gross=30000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    high_income = calculator.calculate_net_income(
        annual_gross=60000,
        tax_class=1,
        children=0,
        church_tax=False
    )

    # Calculate effective tax rates
    low_rate = low_income['income_tax'] / low_income['gross_annual']
    high_rate = high_income['income_tax'] / high_income['gross_annual']

    # Higher income should have higher effective tax rate (progressive)
    assert high_rate > low_rate


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
