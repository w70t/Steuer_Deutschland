"""Settings and language handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import t, i18n
from bot.models.database import AsyncSessionLocal
from bot.models.user import User
from sqlalchemy import select
from loguru import logger
from config import SUPPORTED_LANGUAGES


async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    settings_text = t('settings_menu', lang=user_lang)

    keyboard = [
        [InlineKeyboardButton(t('language', lang=user_lang), callback_data='change_language')],
        [InlineKeyboardButton(t('back', lang=user_lang), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        settings_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu"""
    query = update.callback_query
    await query.answer()

    user_lang = context.user_data.get('language', 'de')

    language_text = t('language_menu', lang=user_lang)

    # Create language buttons (2 per row)
    keyboard = []
    row = []
    for i, lang_code in enumerate(SUPPORTED_LANGUAGES):
        lang_name = i18n.get_language_name(lang_code)
        row.append(InlineKeyboardButton(lang_name, callback_data=f'lang_{lang_code}'))

        if (i + 1) % 2 == 0 or i == len(SUPPORTED_LANGUAGES) - 1:
            keyboard.append(row)
            row = []

    # Back button
    keyboard.append([InlineKeyboardButton(t('back', lang=user_lang), callback_data='settings')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        language_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user language"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Extract language code
    lang_code = query.data.split('_')[1]

    # Update user language in database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if db_user:
            db_user.language = lang_code
            await session.commit()
            logger.info(f"User {user.id} changed language to {lang_code}")

    # Update context
    context.user_data['language'] = lang_code

    # Show confirmation in new language
    confirmation_text = t('language_selected', lang=lang_code)

    # Main menu button
    keyboard = [[InlineKeyboardButton(t('main_menu', lang=lang_code), callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        confirmation_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
