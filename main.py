"""
German Tax Calculator Telegram Bot
Main entry point
"""
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from loguru import logger
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import configuration
from config import settings

# Import handlers
from bot.handlers.start import start_command, main_menu, help_command
from bot.handlers.calculation import (
    start_calculation,
    receive_income,
    receive_tax_class,
    receive_children,
    receive_church_tax,
    cancel_calculation,
    INCOME,
    TAX_CLASS,
    CHILDREN,
    CHURCH_TAX
)
from bot.handlers.settings import settings_menu, language_menu, set_language
from bot.handlers.admin import approve_update, reject_update, send_update_notification
from bot.handlers.history import show_history

# Import services
from bot.services.tax_update_monitor import tax_update_monitor
from bot.models.database import init_db, close_db

# Import error tracking
import sentry_sdk


def setup_logging():
    """Setup logging configuration"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL
    )
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",
        retention="30 days",
        level=settings.LOG_LEVEL
    )


def setup_sentry():
    """Setup Sentry error tracking"""
    if settings.ENABLE_SENTRY and settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,
            environment="production"
        )
        logger.info("Sentry error tracking enabled")


async def check_tax_updates(context):
    """Scheduled task to check for tax updates"""
    logger.info("Checking for tax updates...")

    try:
        updates = await tax_update_monitor.check_for_updates()

        if updates:
            logger.info(f"Found {len(updates)} potential tax updates")

            for update_info in updates:
                # Send notification to admin
                await send_update_notification(context, update_info)
        else:
            logger.info("No new tax updates found")

    except Exception as e:
        logger.error(f"Error checking tax updates: {e}")


async def error_handler(update: Update, context):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

    if settings.ENABLE_SENTRY:
        sentry_sdk.capture_exception(context.error)

    # Notify user
    if update and update.effective_chat:
        try:
            from bot.utils import t
            user_lang = context.user_data.get('language', 'de') if context.user_data else 'de'
            error_text = t('error_occurred', lang=user_lang)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_text
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


def main():
    """Main function to run the bot"""
    # Validate configuration
    settings.validate_config()

    # Setup logging
    setup_logging()
    logger.info("Starting German Tax Calculator Bot...")

    # Setup error tracking
    setup_sentry()

    # Initialize database
    asyncio.run(init_db())
    logger.info("Database initialized")

    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for tax calculation
    calculation_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_calculation, pattern='^calculate$')],
        states={
            INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_income)],
            TAX_CLASS: [CallbackQueryHandler(receive_tax_class, pattern='^tc_')],
            CHILDREN: [CallbackQueryHandler(receive_children, pattern='^children_')],
            CHURCH_TAX: [CallbackQueryHandler(receive_church_tax, pattern='^church_')],
        },
        fallbacks=[CallbackQueryHandler(cancel_calculation, pattern='^main_menu$')],
        allow_reentry=True
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(settings_menu, pattern='^settings$'))
    application.add_handler(CallbackQueryHandler(language_menu, pattern='^change_language$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(show_history, pattern='^history$'))
    application.add_handler(CallbackQueryHandler(approve_update, pattern='^approve_update_'))
    application.add_handler(CallbackQueryHandler(reject_update, pattern='^reject_update_'))
    application.add_handler(calculation_conv)

    # Error handler
    application.add_error_handler(error_handler)

    # Setup scheduler for tax updates monitoring
    if settings.TAX_SOURCES_CHECK_ENABLED:
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            check_tax_updates,
            'interval',
            hours=settings.CHECK_UPDATES_INTERVAL_HOURS,
            args=[application],
            id='tax_updates_check'
        )
        scheduler.start()
        logger.info(f"Tax updates monitoring enabled (every {settings.CHECK_UPDATES_INTERVAL_HOURS} hours)")

    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        asyncio.run(close_db())
        logger.info("Bot shutdown complete")
