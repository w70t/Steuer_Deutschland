"""Tax calculation handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.utils import t
from bot.services import tax_calculator
from bot.models.database import AsyncSessionLocal
from bot.models.user import User
from bot.models.calculation import TaxCalculation
from sqlalchemy import select
from loguru import logger
from datetime import datetime
from config.settings import GERMAN_STATES

# Conversation states
PERIOD, STATE, INCOME, TAX_CLASS, CHILDREN, CHURCH_TAX = range(6)


async def start_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start tax calculation process - ask for calculation period"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Ask for calculation period (monthly or annual)
    period_text = t('select_period', lang=user_lang)

    keyboard = [
        [
            InlineKeyboardButton(t('monthly', lang=user_lang), callback_data='period_monthly'),
            InlineKeyboardButton(t('annual', lang=user_lang), callback_data='period_annual'),
        ],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        period_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return PERIOD


async def receive_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive period selection (monthly/annual)"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract period from callback data
    period = query.data.split('_')[1]  # 'monthly' or 'annual'
    context.user_data['period'] = period

    # Ask for German state (Bundesland)
    state_text = t('select_state', lang=user_lang)

    # Create state selection keyboard (2 columns, 8 rows)
    keyboard = []
    state_codes = list(GERMAN_STATES.keys())

    for i in range(0, len(state_codes), 2):
        row = []
        for j in range(2):
            if i + j < len(state_codes):
                state_code = state_codes[i + j]
                state_name = t(f'state_{state_code}', lang=user_lang)
                row.append(InlineKeyboardButton(state_name, callback_data=f'state_{state_code}'))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        state_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return STATE


async def receive_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive state selection"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract state from callback data
    state_code = query.data.split('_')[1]
    context.user_data['state'] = state_code

    # Save state to user database for future use
    user = update.effective_user
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.state = state_code
            await session.commit()
            logger.info(f"User {user.id} selected state: {state_code}")

    # Ask for gross income (monthly or annual based on period)
    period = context.user_data.get('period', 'annual')
    if period == 'monthly':
        income_text = t('enter_monthly_gross', lang=user_lang)
    else:
        income_text = t('enter_gross_income', lang=user_lang)

    # Cancel button
    keyboard = [[InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        income_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return INCOME


async def receive_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive gross income input"""
    user_lang = context.user_data.get('language', 'de')

    try:
        # Parse income
        income_text = update.message.text.replace(',', '.').replace('€', '').strip()
        income = float(income_text)

        if income <= 0:
            raise ValueError("Income must be positive")

        # Convert monthly to annual if needed
        period = context.user_data.get('period', 'annual')
        if period == 'monthly':
            # User entered monthly, convert to annual for calculation
            annual_income = income * 12
            context.user_data['gross_income'] = annual_income
            context.user_data['entered_monthly'] = income
        else:
            context.user_data['gross_income'] = income

        # Ask for tax class
        tax_class_text = t('select_tax_class', lang=user_lang)

        keyboard = [
            [
                InlineKeyboardButton(t('tax_class_1', lang=user_lang), callback_data='tc_1'),
                InlineKeyboardButton(t('tax_class_2', lang=user_lang), callback_data='tc_2'),
            ],
            [
                InlineKeyboardButton(t('tax_class_3', lang=user_lang), callback_data='tc_3'),
                InlineKeyboardButton(t('tax_class_4', lang=user_lang), callback_data='tc_4'),
            ],
            [
                InlineKeyboardButton(t('tax_class_5', lang=user_lang), callback_data='tc_5'),
                InlineKeyboardButton(t('tax_class_6', lang=user_lang), callback_data='tc_6'),
            ],
            [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            tax_class_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

        return TAX_CLASS

    except ValueError:
        error_text = t('invalid_amount', lang=user_lang)
        await update.message.reply_text(error_text)
        return INCOME


async def receive_tax_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive tax class selection"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract tax class from callback data
    tax_class = int(query.data.split('_')[1])
    context.user_data['tax_class'] = tax_class

    # Ask for children
    children_text = t('ask_children', lang=user_lang)

    keyboard = [
        [
            InlineKeyboardButton('0', callback_data='children_0'),
            InlineKeyboardButton('1', callback_data='children_1'),
            InlineKeyboardButton('2', callback_data='children_2'),
        ],
        [
            InlineKeyboardButton('3', callback_data='children_3'),
            InlineKeyboardButton('4', callback_data='children_4'),
            InlineKeyboardButton('5+', callback_data='children_5'),
        ],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        children_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return CHILDREN


async def receive_children(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive number of children"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract number of children
    children = int(query.data.split('_')[1])
    context.user_data['children'] = children

    # Ask for church tax
    church_text = t('ask_church_tax', lang=user_lang)

    keyboard = [
        [
            InlineKeyboardButton(t('yes', lang=user_lang), callback_data='church_yes'),
            InlineKeyboardButton(t('no', lang=user_lang), callback_data='church_no'),
        ],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        church_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return CHURCH_TAX


async def receive_church_tax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive church tax selection and perform calculation"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract church tax choice
    church_tax = query.data == 'church_yes'
    context.user_data['church_tax'] = church_tax

    # Show calculating message
    calculating_text = t('calculating', lang=user_lang)
    await query.edit_message_text(calculating_text)

    # Perform calculation
    gross_income = context.user_data['gross_income']
    tax_class = context.user_data['tax_class']
    children = context.user_data['children']
    state = context.user_data.get('state', 'BE')  # Default to Berlin if not set

    result = tax_calculator.calculate_net_income(
        annual_gross=gross_income,
        tax_class=tax_class,
        children=children,
        church_tax=church_tax,
        state=state
    )

    # Save calculation to database
    user = update.effective_user
    async with AsyncSessionLocal() as session:
        # Get user
        db_result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = db_result.scalar_one_or_none()

        if db_user:
            # Create calculation record
            calculation = TaxCalculation(
                user_id=db_user.id,
                gross_income=result['gross_annual'],
                tax_class=tax_class,
                children=children,
                church_tax=church_tax,
                state=state,
                income_tax=result['income_tax'],
                solidarity_surcharge=result['solidarity_surcharge'],
                church_tax_amount=result['church_tax'],
                health_insurance=result['health_insurance'],
                pension_insurance=result['pension_insurance'],
                unemployment_insurance=result['unemployment_insurance'],
                care_insurance=result['care_insurance'],
                total_deductions=result['total_deductions'],
                net_income=result['net_annual'],
                calculation_details=result,
                tax_year=datetime.now().year
            )
            session.add(calculation)
            await session.commit()

    # Format result message
    result_text = t(
        'calculation_result',
        lang=user_lang,
        year=result['year'],
        gross=f"{result['gross_annual']:,.2f}",
        income_tax=f"{result['income_tax']:,.2f}",
        soli=f"{result['solidarity_surcharge']:,.2f}",
        church=f"{result['church_tax']:,.2f}",
        health=f"{result['health_insurance']:,.2f}",
        pension=f"{result['pension_insurance']:,.2f}",
        unemployment=f"{result['unemployment_insurance']:,.2f}",
        care=f"{result['care_insurance']:,.2f}",
        total_deductions=f"{result['total_deductions']:,.2f}",
        net=f"{result['net_annual']:,.2f}",
        monthly_gross=f"{result['gross_monthly']:,.2f}",
        monthly_net=f"{result['net_monthly']:,.2f}"
    )

    # Buttons
    keyboard = [
        [InlineKeyboardButton(t('calculate_tax', lang=user_lang), callback_data='calculate')],
        [InlineKeyboardButton(t('main_menu', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        result_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    # Clear context
    context.user_data.clear()
    context.user_data['language'] = user_lang

    return ConversationHandler.END


async def cancel_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel calculation and return to main menu"""
    query = update.callback_query
    await query.answer()

    # Import here to avoid circular import
    from .start import main_menu
    return await main_menu(update, context)
