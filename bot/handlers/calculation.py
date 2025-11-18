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
from config.settings import (
    GERMAN_STATES,
    TAX_CLASSES,
    EMPLOYMENT_TYPES,
    HEALTH_INSURANCE_COMPANIES,
    KINDERFREIBETRAG_OPTIONS,
    PRIVATE_HEALTH_INSURANCE
)

# Conversation states
(PERIOD, STATE, EMPLOYMENT_TYPE, INCOME, TAX_CLASS, CHILDREN_HAS,
 CHILDREN_COUNT, KINDERFREIBETRAG, AGE_GROUP, HEALTH_INSURANCE_TYPE,
 HEALTH_INSURANCE_COMPANY, PRIVATE_INSURANCE, CHURCH_TAX) = range(13)


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

    # Ask for German state (Bundesland) - now includes BE_WEST and BE_EAST
    state_text = t('select_state', lang=user_lang)

    # Create state selection keyboard (2 columns)
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
    """Receive state selection and ask for employment type"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract state from callback data
    state_code = query.data.split('_', 1)[1]  # Handle BE_WEST, BE_EAST
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

    # Ask for employment type (Beschäftigungsart)
    employment_text = t('select_employment_type', lang=user_lang)

    keyboard = [
        [InlineKeyboardButton(
            t('employment_standard', lang=user_lang),
            callback_data='emp_standard'
        )],
        [InlineKeyboardButton(
            t('employment_trainee', lang=user_lang),
            callback_data='emp_trainee'
        )],
        [InlineKeyboardButton(
            t('employment_civil_servant', lang=user_lang),
            callback_data='emp_civil_servant'
        )],
        [InlineKeyboardButton(
            t('employment_self_employed', lang=user_lang),
            callback_data='emp_self_employed'
        )],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        employment_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return EMPLOYMENT_TYPE


async def receive_employment_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive employment type and ask for income"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract employment type from callback data
    employment_type = query.data.split('_', 1)[1]  # 'standard', 'trainee', etc.
    context.user_data['employment_type'] = employment_type

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
    """Receive gross income input and ask for tax class"""
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

        # Ask for tax class with detailed descriptions
        tax_class_text = t('select_tax_class', lang=user_lang)

        keyboard = []
        for tc_num in range(1, 7):
            tc_data = TAX_CLASSES[tc_num]
            # Use name from TAX_CLASSES dict
            button_text = t(f'tax_class_{tc_num}_detailed', lang=user_lang)
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'tc_{tc_num}')])

        keyboard.append([InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')])
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
    """Receive tax class selection and ask about children"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract tax class from callback data
    tax_class = int(query.data.split('_')[1])
    context.user_data['tax_class'] = tax_class

    # Ask if user has children
    children_has_text = t('ask_has_children', lang=user_lang)

    keyboard = [
        [
            InlineKeyboardButton(t('yes', lang=user_lang), callback_data='has_children_yes'),
            InlineKeyboardButton(t('no', lang=user_lang), callback_data='has_children_no'),
        ],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        children_has_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return CHILDREN_HAS


async def receive_children_has(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive if user has children"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')
    has_children = query.data == 'has_children_yes'

    if not has_children:
        # No children - set defaults and move to age group
        context.user_data['children_count'] = 0
        context.user_data['kinderfreibetrag'] = 0.0
        return await ask_age_group(query, context)

    # Ask for number of children under 25
    children_count_text = t('ask_children_count', lang=user_lang)

    keyboard = [
        [
            InlineKeyboardButton('0', callback_data='children_count_0'),
            InlineKeyboardButton('1', callback_data='children_count_1'),
            InlineKeyboardButton('2', callback_data='children_count_2'),
        ],
        [
            InlineKeyboardButton('3', callback_data='children_count_3'),
            InlineKeyboardButton('4', callback_data='children_count_4'),
            InlineKeyboardButton('5+', callback_data='children_count_5'),
        ],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        children_count_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return CHILDREN_COUNT


async def receive_children_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive children count and ask for Kinderfreibetrag"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract number of children
    children_count = int(query.data.split('_')[2])
    context.user_data['children_count'] = children_count

    # Ask for Kinderfreibetrag
    kinderfreibetrag_text = t('ask_kinderfreibetrag', lang=user_lang)

    # Create keyboard with options 0.0 to 6.0 in 0.5 steps (4 columns)
    keyboard = []
    options = KINDERFREIBETRAG_OPTIONS
    for i in range(0, len(options), 4):
        row = []
        for j in range(4):
            if i + j < len(options):
                value = options[i + j]
                row.append(InlineKeyboardButton(
                    str(value),
                    callback_data=f'kfb_{str(value).replace(".", "_")}'
                ))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        kinderfreibetrag_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return KINDERFREIBETRAG


async def receive_kinderfreibetrag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive Kinderfreibetrag and ask for age group"""
    query = update.callback_query
    await query.answer()

    # Extract Kinderfreibetrag value
    kfb_str = query.data.split('_')[1]  # e.g., "1_5" for 1.5
    kinderfreibetrag = float(kfb_str.replace('_', '.'))
    context.user_data['kinderfreibetrag'] = kinderfreibetrag

    return await ask_age_group(query, context)


async def ask_age_group(query, context: ContextTypes.DEFAULT_TYPE):
    """Ask for age group (affects care insurance)"""
    user_lang = context.user_data.get('language', 'de')

    age_text = t('select_age_group', lang=user_lang)

    keyboard = [
        [InlineKeyboardButton(
            t('age_under_23', lang=user_lang),
            callback_data='age_under_23'
        )],
        [InlineKeyboardButton(
            t('age_over_23_children', lang=user_lang),
            callback_data='age_over_23_children'
        )],
        [InlineKeyboardButton(
            t('age_over_23_no_children', lang=user_lang),
            callback_data='age_over_23_no_children'
        )],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        age_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return AGE_GROUP


async def receive_age_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive age group and ask for health insurance type"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract age group
    age_group = query.data.split('_', 1)[1]  # 'under_23', 'over_23_children', 'over_23_no_children'
    context.user_data['age_group'] = age_group

    # Ask for health insurance type
    health_type_text = t('select_health_insurance_type', lang=user_lang)

    keyboard = [
        [InlineKeyboardButton(
            t('health_insurance_public', lang=user_lang),
            callback_data='health_type_public'
        )],
        [InlineKeyboardButton(
            t('health_insurance_private', lang=user_lang),
            callback_data='health_type_private'
        )],
        [InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        health_type_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    return HEALTH_INSURANCE_TYPE


async def receive_health_insurance_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive health insurance type"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Extract health insurance type
    health_type = query.data.split('_')[2]  # 'public' or 'private'
    context.user_data['health_insurance_type'] = health_type

    if health_type == 'public':
        # Show health insurance companies (Gesetzlich)
        health_company_text = t('select_health_insurance_company', lang=user_lang)

        # Create keyboard with all 23 companies (2 columns)
        keyboard = []
        companies = list(HEALTH_INSURANCE_COMPANIES.items())

        for i in range(0, len(companies), 2):
            row = []
            for j in range(2):
                if i + j < len(companies):
                    company_code, company_data = companies[i + j]
                    company_name = t(f'health_company_{company_code}', lang=user_lang)
                    employee_share = company_data['employee_share']
                    button_text = f"{company_name} ({employee_share}%)"
                    row.append(InlineKeyboardButton(button_text, callback_data=f'hc_{company_code}'))
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton(t('cancel', lang=user_lang), callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            health_company_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

        return HEALTH_INSURANCE_COMPANY
    else:
        # Private insurance - ask for church tax directly
        # Note: For private insurance, we'll use default values in calculation
        context.user_data['health_insurance_company'] = 'private'
        return await ask_church_tax(query, context)


async def receive_health_insurance_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive health insurance company and ask for church tax"""
    query = update.callback_query
    await query.answer()

    # Extract company code
    company_code = query.data.split('_')[1]
    context.user_data['health_insurance_company'] = company_code

    return await ask_church_tax(query, context)


async def ask_church_tax(query, context: ContextTypes.DEFAULT_TYPE):
    """Ask for church tax"""
    user_lang = context.user_data.get('language', 'de')

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

    # Gather all calculation parameters
    gross_income = context.user_data['gross_income']
    tax_class = context.user_data['tax_class']
    children_count = context.user_data.get('children_count', 0)
    kinderfreibetrag = context.user_data.get('kinderfreibetrag', 0.0)
    state = context.user_data.get('state', 'BE_WEST')
    employment_type = context.user_data.get('employment_type', 'standard')
    age_group = context.user_data.get('age_group', 'under_23')
    health_insurance_company = context.user_data.get('health_insurance_company', 'tk')

    # Perform calculation
    result = tax_calculator.calculate_net_income(
        annual_gross=gross_income,
        tax_class=tax_class,
        children=children_count,
        kinderfreibetrag=kinderfreibetrag,
        church_tax=church_tax,
        state=state,
        employment_type=employment_type,
        age_group=age_group,
        health_insurance_company=health_insurance_company
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
                children=children_count,
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

    # Clear context but preserve language
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
