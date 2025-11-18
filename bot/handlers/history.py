"""Calculation history handler"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import t
from bot.models.database import AsyncSessionLocal
from bot.models.user import User
from bot.models.calculation import TaxCalculation
from sqlalchemy import select
from loguru import logger


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's calculation history"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    user_lang = context.user_data.get('language', 'de')

    # Get user's calculations from database
    async with AsyncSessionLocal() as session:
        # Get user
        user_result = await session.execute(
            select(User).where(User.telegram_id == user.id)
        )
        db_user = user_result.scalar_one_or_none()

        if not db_user:
            await query.edit_message_text(t('error_occurred', lang=user_lang))
            return

        # Get calculations
        calc_result = await session.execute(
            select(TaxCalculation)
            .where(TaxCalculation.user_id == db_user.id)
            .order_by(TaxCalculation.created_at.desc())
            .limit(10)
        )
        calculations = calc_result.scalars().all()

        if not calculations:
            # No calculations yet
            no_calc_text = t('no_calculations', lang=user_lang)
            keyboard = [[InlineKeyboardButton(t('back', lang=user_lang), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                no_calc_text,
                reply_markup=reply_markup
            )
            return

        # Format calculation history
        history_text = f"📋 <b>{t('my_calculations', lang=user_lang)}</b>\n\n"

        for i, calc in enumerate(calculations, 1):
            date = calc.created_at.strftime('%d.%m.%Y %H:%M')
            history_text += (
                f"{i}. <b>{date}</b>\n"
                f"   💰 {calc.gross_income:,.0f}€ → {calc.net_income:,.0f}€\n"
                f"   📑 {t(f'tax_class_{calc.tax_class}', lang=user_lang)}\n"
                f"   💸 {calc.total_deductions:,.0f}€ ({t('total_deductions', lang=user_lang)})\n\n"
            )

        # Back button
        keyboard = [[InlineKeyboardButton(t('back', lang=user_lang), callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            history_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
