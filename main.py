import logging
import asyncio
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import Database
from handlers import BotHandlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления {update}: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "😔 Произошла ошибка при обработке команды. Попробуйте позже."
        )

async def main():
    """Главная функция"""
    try:
        # Инициализируем базу данных и обработчики
        db = Database()
        handlers = BotHandlers(db)
        
        # Создаем приложение
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Настраиваем обработчики команд
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("tits", handlers.tits_command))
        application.add_handler(CommandHandler("stats", handlers.stats_command))
        application.add_handler(CommandHandler("top", handlers.top_command))
        application.add_handler(CommandHandler("history", handlers.history_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("reset_all", handlers.reset_all_command))
        
        # Обработчик неизвестных команд (должен быть последним)
        application.add_handler(
            MessageHandler(filters.COMMAND, handlers.unknown_command)
        )
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        logger.info("Обработчики команд настроены")
        
        # Настраиваем команды бота
        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("tits", "Изменить размер груди"),
            BotCommand("stats", "Показать статистику"),
            BotCommand("top", "Топ пользователей"),
            BotCommand("history", "История изменений"),
            BotCommand("help", "Справка")
        ]
        
        await application.bot.set_my_commands(commands)
        logger.info("Команды бота настроены")
        
        # Запускаем бота
        logger.info("Бот запускается...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Ждем завершения
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
