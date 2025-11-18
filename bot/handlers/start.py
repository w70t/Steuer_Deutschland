"""Start and main menu handlers"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import t
from bot.models.database import AsyncSessionLocal
from bot.models.user import User
from sqlalchemy import select
from loguru import logger


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Check if user exists
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = result.scalar_one_or_none()

        if not db_user:
            # New user - start onboarding (language selection + terms)
            from .onboarding import choose_language
            await choose_language(update, context)
            return

        user_lang = db_user.language

    # Existing user - show welcome and main menu
    context.user_data['language'] = user_lang

    # Welcome message
    welcome_text = t('welcome', lang=user_lang)

    # Main menu keyboard
    keyboard = [
        [InlineKeyboardButton(t('calculate_tax', lang=user_lang), callback_data='calculate')],
        [InlineKeyboardButton(t('my_calculations', lang=user_lang), callback_data='history')],
        [
            InlineKeyboardButton(t('settings', lang=user_lang), callback_data='settings'),
            InlineKeyboardButton(t('help', lang=user_lang), callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_main_menu(query_or_update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu (can be called with query or update)"""
    user_lang = context.user_data.get('language', 'de')

    # Main menu text
    menu_text = t('main_menu', lang=user_lang)

    # Main menu keyboard
    keyboard = [
        [InlineKeyboardButton(t('calculate_tax', lang=user_lang), callback_data='calculate')],
        [InlineKeyboardButton(t('my_calculations', lang=user_lang), callback_data='history')],
        [
            InlineKeyboardButton(t('settings', lang=user_lang), callback_data='settings'),
            InlineKeyboardButton(t('help', lang=user_lang), callback_data='help')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Check if it's a CallbackQuery or Update
    if hasattr(query_or_update, 'edit_message_text'):
        # It's a CallbackQuery
        await query_or_update.edit_message_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        # It's an Update, send new message
        await query_or_update.message.reply_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    query = update.callback_query
    await query.answer()

    await show_main_menu(query, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help command"""
    query = update.callback_query
    if query:
        await query.answer()

    user_lang = context.user_data.get('language', 'de')
    help_text = t('help_text', lang=user_lang)

    # Back button
    keyboard = [[InlineKeyboardButton(t('back', lang=user_lang), callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
