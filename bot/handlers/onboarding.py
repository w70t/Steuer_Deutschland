"""Onboarding handlers for language selection and terms acceptance"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import t, i18n
from bot.models.database import AsyncSessionLocal
from bot.models.user import User
from sqlalchemy import select
from loguru import logger


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection at first start"""
    user = update.effective_user

    # Welcome message asking to choose language
    welcome_text = "🇩🇪 Willkommen! | Welcome! | أهلاً!\n\n🌍 Bitte wählen Sie Ihre Sprache:\nPlease select your language:\nالرجاء اختيار لغتك:"

    # Language selection keyboard (2 columns)
    keyboard = []
    languages = [
        ('de', '🇩🇪 Deutsch'),
        ('ar', '🇸🇦 العربية'),
        ('tr', '🇹🇷 Türkçe'),
        ('pl', '🇵🇱 Polski'),
        ('ru', '🇷🇺 Русский'),
        ('it', '🇮🇹 Italiano'),
        ('ro', '🇷🇴 Română'),
        ('en', '🇬🇧 English'),
        ('el', '🇬🇷 Ελληνικά'),
        ('hr', '🇭🇷 Hrvatski'),
    ]

    # Create 2 columns
    for i in range(0, len(languages), 2):
        row = []
        for j in range(2):
            if i + j < len(languages):
                lang_code, lang_name = languages[i + j]
                row.append(InlineKeyboardButton(lang_name, callback_data=f'setlang_{lang_code}'))
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )


async def set_initial_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set language and show terms and conditions"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Extract language code
    lang_code = query.data.split('_')[1]

    # Store language in context
    context.user_data['language'] = lang_code
    context.user_data['onboarding_lang'] = lang_code

    # Update or create user in database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            # Create new user
            db_user = User(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language=lang_code
            )
            session.add(db_user)
        else:
            # Update language
            db_user.language = lang_code

        await session.commit()
        logger.info(f"User {user.id} selected language: {lang_code}")

    # Show terms and conditions
    await show_terms(update, context, lang_code)


async def show_terms(update: Update, context: ContextTypes.DEFAULT_TYPE, lang_code: str):
    """Show terms and conditions"""
    query = update.callback_query

    # Terms text
    terms_text = t('terms_and_conditions', lang=lang_code)

    # Accept/Decline buttons
    keyboard = [
        [
            InlineKeyboardButton(t('accept_terms', lang=lang_code), callback_data='terms_accept'),
            InlineKeyboardButton(t('decline_terms', lang=lang_code), callback_data='terms_decline')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        terms_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def accept_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle terms acceptance"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_lang = context.user_data.get('language', 'de')

    # Mark terms as accepted in database
    from datetime import datetime
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.terms_accepted = True
            db_user.terms_accepted_at = datetime.utcnow()
            await session.commit()
            logger.info(f"User {user.id} accepted terms at {datetime.utcnow()}")

    # Show acceptance message
    acceptance_text = t('terms_accepted', lang=user_lang)

    # Continue to main menu
    from .start import show_main_menu
    await query.edit_message_text(acceptance_text, parse_mode='HTML')

    # Wait a moment and show main menu
    import asyncio
    await asyncio.sleep(1)
    await show_main_menu(query, context)


async def decline_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle terms decline"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Show decline message with option to reconsider
    decline_text = t('terms_declined_message', lang=user_lang)

    keyboard = [
        [InlineKeyboardButton(t('reconsider_terms', lang=user_lang), callback_data='terms_reconsider')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        decline_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    logger.info(f"User {update.effective_user.id} declined terms")


async def reconsider_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show terms again when user reconsiders"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    # Show terms again
    await show_terms(update, context, user_lang)
