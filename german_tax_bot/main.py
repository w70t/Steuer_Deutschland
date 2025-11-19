# main.py
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- Calculation Logic ---
def calculate_net_income(gross_monthly: float) -> dict:
    # Constants for 2024 (Tax Class 1, childless, public health insurance)
    PENSION_UNEMPLOYMENT_CEILING = 7550.0
    HEALTH_CARE_CEILING = 5175.0
    PENSION_RATE = 0.093
    UNEMPLOYMENT_RATE = 0.013
    HEALTH_INSURANCE_RATE = 0.0815  # 7.3% base + half of 1.7% avg. additional contribution
    CARE_INSURANCE_RATE = 0.023     # 1.7% base + 0.6% surcharge for childless over 23

    # Social Security Calculations
    pension_base = min(gross_monthly, PENSION_UNEMPLOYMENT_CEILING)
    health_base = min(gross_monthly, HEALTH_CARE_CEILING)

    pension_insurance = pension_base * PENSION_RATE
    unemployment_insurance = pension_base * UNEMPLOYMENT_RATE
    health_insurance = health_base * HEALTH_INSURANCE_RATE
    care_insurance = health_base * CARE_INSURANCE_RATE
    total_social = pension_insurance + unemployment_insurance + health_insurance + care_insurance

    # Income Tax Calculation
    gross_annual = gross_monthly * 12
    # Vorsorgepauschale (simplified as total social contributions)
    # Arbeitnehmerpauschbetrag (1230) + Sonderausgabenpauschale (36)
    taxable_income = gross_annual - (total_social * 12) - 1230 - 36

    income_tax_annual = 0
    if taxable_income <= 11604:
        income_tax_annual = 0
    elif taxable_income <= 17005:
        y = (taxable_income - 11604) / 10000
        income_tax_annual = (1088.67 * y + 1400) * y
    elif taxable_income <= 66760:
        x = (taxable_income - 17005) / 10000
        income_tax_annual = (206.43 * x + 2397) * x + 938.24
    elif taxable_income <= 277825:
        income_tax_annual = 0.42 * taxable_income - 10253.36
    else:
        income_tax_annual = 0.45 * taxable_income - 18588.11

    solidarity_surcharge_annual = 0
    if income_tax_annual > 18130:
        solidarity_surcharge_annual = income_tax_annual * 0.055

    income_tax_monthly = income_tax_annual / 12
    solidarity_surcharge_monthly = solidarity_surcharge_annual / 12
    total_tax = income_tax_monthly + solidarity_surcharge_monthly

    net_monthly = gross_monthly - total_social - total_tax

    return {
        "net_monthly": net_monthly,
        "income_tax": income_tax_monthly,
        "solidarity_surcharge": solidarity_surcharge_monthly,
        "pension_insurance": pension_insurance,
        "unemployment_insurance": unemployment_insurance,
        "health_insurance": health_insurance,
        "care_insurance": care_insurance,
        "total_social_contributions": total_social,
    }

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message."""
    await update.message.reply_text(
        'Welcome to the German Net Income Bot!\\n'
        'Use /calculate to start.'
    )

async def calculate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asks for gross income."""
    await update.message.reply_text('Please enter your gross monthly income in EUR:')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the user's income input and calculates the net income."""
    try:
        gross_income = float(update.message.text)
        if gross_income < 0:
            await update.message.reply_text('Income cannot be negative. Please enter a valid amount.')
            return

        results = calculate_net_income(gross_income)

        response_message = (
            f"Calculation for a gross monthly income of €{gross_income:,.2f}:\\n\\n"
            f"<b>Net Monthly Income: €{results['net_monthly']:,.2f}</b>\\n\\n"
            f"<u>Deductions:</u>\\n"
            f"  - Income Tax: €{results['income_tax']:,.2f}\\n"
            f"  - Solidarity Surcharge: €{results['solidarity_surcharge']:,.2f}\\n"
            f"  - Health Insurance: €{results['health_insurance']:,.2f}\\n"
            f"  - Pension Insurance: €{results['pension_insurance']:,.2f}\\n"
            f"  - Unemployment Insurance: €{results['unemployment_insurance']:,.2f}\\n"
            f"  - Care Insurance: €{results['care_insurance']:,.2f}\\n\\n"
            f"<i>Disclaimer: This is an approximation based on 2024 values for a single person (tax class 1) without children and no church tax. Actual values may vary.</i>"
        )
        await update.message.reply_html(response_message)

    except ValueError:
        await update.message.reply_text('Please enter a valid number for your income.')


def main() -> None:
    """Start the bot."""
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        # For local development, you might use a .env file or another method.
        # This is a placeholder for when the token isn't set.
        print("ERROR: TELEGRAM_TOKEN environment variable not set.")
        return

    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("calculate", calculate_command))
    # Add a message handler for non-command text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
