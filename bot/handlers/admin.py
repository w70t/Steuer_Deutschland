"""Admin handlers for tax update notifications and approvals"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.utils import t
from bot.models.database import AsyncSessionLocal
from bot.models.tax_update import TaxUpdate
from bot.models.user import User
from sqlalchemy import select
from loguru import logger
from datetime import datetime
from config import ADMIN_TELEGRAM_ID
import json


async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    if user_id == ADMIN_TELEGRAM_ID:
        return True

    # Check database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        db_user = result.scalar_one_or_none()
        return db_user and db_user.is_admin


async def send_update_notification(context: ContextTypes.DEFAULT_TYPE, update_info: dict):
    """
    Send tax update notification to admin

    Args:
        context: Bot context
        update_info: Update information dictionary
    """
    # Save update to database
    async with AsyncSessionLocal() as session:
        tax_update = TaxUpdate(
            title=update_info['title'],
            description=update_info.get('description', ''),
            source_url=update_info['source_url'],
            source_name=update_info['source_name'],
            update_type=update_info['update_type'],
            changes=update_info.get('changes', {}),
            effective_date=update_info.get('effective_date'),
            admin_notified=True,
            admin_notified_at=datetime.utcnow()
        )
        session.add(tax_update)
        await session.commit()
        update_id = tax_update.id

    # Format changes
    changes_text = update_info.get('description', 'No details available')
    if isinstance(update_info.get('changes'), dict):
        changes_text = '\n'.join([f"• {k}: {v}" for k, v in update_info['changes'].items()])

    effective_date = update_info.get('effective_date', 'Not specified')
    if isinstance(effective_date, datetime):
        effective_date = effective_date.strftime('%d.%m.%Y')

    # Get admin language (default to German)
    admin_lang = 'de'
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == ADMIN_TELEGRAM_ID)
        )
        admin_user = result.scalar_one_or_none()
        if admin_user:
            admin_lang = admin_user.language

    # Create notification message
    notification_text = t(
        'admin_update_notification',
        lang=admin_lang,
        title=update_info['title'],
        source=update_info['source_name'],
        type=update_info['update_type'],
        url=update_info['source_url'],
        changes=changes_text,
        effective_date=effective_date
    )

    # Approval buttons
    keyboard = [
        [
            InlineKeyboardButton(
                t('approve_update', lang=admin_lang),
                callback_data=f'approve_update_{update_id}'
            ),
            InlineKeyboardButton(
                t('reject_update', lang=admin_lang),
                callback_data=f'reject_update_{update_id}'
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=notification_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        logger.info(f"Tax update notification sent to admin: {update_info['title']}")
    except Exception as e:
        logger.error(f"Failed to send update notification to admin: {e}")


async def approve_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle update approval"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Check if user is admin
    if not await is_admin(user.id):
        await query.edit_message_text(t('admin_only', lang='de'))
        return

    # Extract update ID
    update_id = int(query.data.split('_')[2])

    # Update database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TaxUpdate).where(TaxUpdate.id == update_id)
        )
        tax_update = result.scalar_one_or_none()

        if tax_update:
            tax_update.approved_by_admin = True
            tax_update.approved_at = datetime.utcnow()
            tax_update.applied = True
            tax_update.applied_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Tax update {update_id} approved and applied by admin {user.id}")

            # Get user language
            user_result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = user_result.scalar_one_or_none()
            user_lang = db_user.language if db_user else 'de'

            # Show confirmation
            confirmation_text = t('update_approved', lang=user_lang)
            await query.edit_message_text(confirmation_text)

            # TODO: Apply the update to tax calculation parameters
            # This would involve updating the config or database with new values


async def reject_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle update rejection"""
    query = update.callback_query
    await query.answer()

    user = update.effective_user

    # Check if user is admin
    if not await is_admin(user.id):
        await query.edit_message_text(t('admin_only', lang='de'))
        return

    # Extract update ID
    update_id = int(query.data.split('_')[2])

    # Update database
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(TaxUpdate).where(TaxUpdate.id == update_id)
        )
        tax_update = result.scalar_one_or_none()

        if tax_update:
            tax_update.approved_by_admin = False
            tax_update.approved_at = datetime.utcnow()
            await session.commit()

            logger.info(f"Tax update {update_id} rejected by admin {user.id}")

            # Get user language
            user_result = await session.execute(
                select(User).where(User.telegram_id == user.id)
            )
            db_user = user_result.scalar_one_or_none()
            user_lang = db_user.language if db_user else 'de'

            # Show confirmation
            confirmation_text = t('update_rejected', lang=user_lang)
            await query.edit_message_text(confirmation_text)
