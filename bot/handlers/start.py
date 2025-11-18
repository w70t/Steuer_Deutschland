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

    # Get or create user in database
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
                language='de'
            )
            session.add(db_user)
            await session.commit()
            logger.info(f"New user registered: {user.id}")

        user_lang = db_user.language

    # Store user language in context
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


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    query = update.callback_query
    await query.answer()

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

    await query.edit_message_text(
        menu_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


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
