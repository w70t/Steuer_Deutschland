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
from bot.utils.error_tracker import error_tracker, track_error


def setup_logging():
    """Setup logging configuration with enhanced error tracking"""
    logger.remove()

    # Console logging with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # Main log file
    logger.add(
        settings.LOG_FILE,
        rotation="10 MB",
        retention="30 days",
        level=settings.LOG_LEVEL,
        encoding='utf-8',
        enqueue=True
    )

    # Error-specific log file with detailed information
    logger.add(
        settings.ERROR_LOG_FILE,
        rotation="5 MB",
        retention="90 days",
        level="ERROR",
        encoding='utf-8',
        backtrace=True,
        diagnose=True,
        enqueue=True
    )

    logger.info("✅ Logging system initialized with enhanced error tracking")


def show_error_statistics():
    """عرض إحصائيات الأخطاء عند بدء التشغيل"""
    try:
        stats = error_tracker.get_error_statistics()
        if stats.get('total', 0) > 0:
            logger.warning(f"📊 Previous errors detected: {stats['total']}")
            if stats.get('most_common_error'):
                logger.warning(f"   Most common: {stats['most_common_error']}")
            if stats.get('most_problematic_operation'):
                logger.warning(f"   Problematic operation: {stats['most_problematic_operation']}")
    except Exception as e:
        logger.debug(f"Could not load error statistics: {e}")


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
    """معالج الأخطاء مع تتبع محلي مفصل"""
    # جمع معلومات السياق
    error_context = {
        'update_type': type(update).__name__ if update else None,
        'chat_id': update.effective_chat.id if update and update.effective_chat else None,
        'message_text': update.message.text if update and update.message else None,
        'callback_data': update.callback_query.data if update and update.callback_query else None,
    }

    user_id = update.effective_user.id if update and update.effective_user else None

    # تتبع الخطأ بشكل مفصل
    track_error(
        error=context.error,
        context=error_context,
        user_id=user_id,
        operation='telegram_bot_handler'
    )

    # إشعار المستخدم
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


async def main():
    """Main function to run the bot"""
    # Validate configuration
    settings.validate_config()

    # Setup logging
    setup_logging()
    logger.info("🚀 Starting German Tax Calculator Bot...")

    # Show previous error statistics
    show_error_statistics()

    # Initialize database
    await init_db()
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
        name="tax_calculation",
        allow_reentry=True,
        per_chat=True,
        per_user=True,
        per_message=False
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

    # Register cleanup handler
    async def post_shutdown(app):
        """Cleanup after bot shutdown"""
        await close_db()
        logger.info("Database connections closed")

    application.post_shutdown = post_shutdown

    # Setup scheduler for tax updates monitoring after initialization
    async def post_init(app):
        """Initialize scheduler after event loop is ready"""
        if settings.TAX_SOURCES_CHECK_ENABLED:
            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                check_tax_updates,
                'interval',
                hours=settings.CHECK_UPDATES_INTERVAL_HOURS,
                args=[app],
                id='tax_updates_check'
            )
            scheduler.start()
            logger.info(f"Tax updates monitoring enabled (every {settings.CHECK_UPDATES_INTERVAL_HOURS} hours)")

    application.post_init = post_init

    # Start bot
    logger.info("Bot started successfully!")

    # Initialize and run
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep the bot running
    try:
        # Run until interrupted
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received stop signal")
    finally:
        # Cleanup
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == '__main__':
    try:
        # Fix for Python 3.10+ event loop policy on Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        track_error(
            error=e,
            context={'location': 'main_startup'},
            operation='bot_initialization'
        )
        sys.exit(1)
    finally:
        logger.info("Bot shutdown complete")
