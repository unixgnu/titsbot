import logging
import math
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from game_logic import GameLogic
from config import ENFORCE_COOLDOWN, COOLDOWN_SECONDS, ADMIN_USER_IDS
from datetime import datetime, timezone


def _parse_sqlite_timestamp(timestamp_str: str) -> datetime:
    """Парсит TIMESTAMP из SQLite в timezone-aware UTC datetime."""
    # SQLite CURRENT_TIMESTAMP хранит в формате 'YYYY-MM-DD HH:MM:SS' в UTC
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        # На всякий случай пробуем ISO-форматы
        try:
            # Обработка 'Z' → '+00:00'
            normalized = timestamp_str.replace("Z", "+00:00")
            dt2 = datetime.fromisoformat(normalized)
            if dt2.tzinfo is None:
                dt2 = dt2.replace(tzinfo=timezone.utc)
            return dt2.astimezone(timezone.utc)
        except Exception as _:
            # Если совсем не распарсили — пробросим исключение
            raise


def _format_remaining(seconds_total: int) -> str:
    """Форматирует остаток времени как 'H:MM' без секунд, минуты округляются вверх."""
    if seconds_total < 0:
        seconds_total = 0
    hours = seconds_total // 3600
    leftover = seconds_total % 3600
    # Округляем минуты вверх, если есть оставшиеся секунды
    minutes = math.ceil(leftover / 60) if leftover else 0
    if minutes == 60:
        hours += 1
        minutes = 0
    return f"{hours}:{minutes:02d}"

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, db: Database):
        self.db = db
        self.game_logic = GameLogic()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Сохраняем пользователя и чат в базе
        user_data = self.db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        self.db.get_or_create_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title
        )
        
        welcome_message = (
            f"Привет, {user.first_name}!\n"
            f"Текущий размер: {user_data['breast_size']} ("
            f"{self.game_logic.get_size_description(user_data['breast_size'])})\n"
            f"Команды: /tits /stats /top /history /help"
        )
        
        await update.message.reply_text(welcome_message)
    
    async def tits_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /tits"""
        user = update.effective_user
        chat = update.effective_chat
        
        # Получаем или создаем пользователя
        user_data = self.db.get_or_create_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Получаем или создаем чат
        self.db.get_or_create_chat(
            chat_id=chat.id,
            chat_type=chat.type,
            title=chat.title
        )
        
        # Проверка кулдауна (если включен)
        if ENFORCE_COOLDOWN:
            last_used_str = self.db.get_last_tits_usage(user.id)
            if last_used_str:
                try:
                    # TIMESTAMP в БД считаем как UTC
                    last_used_dt = _parse_sqlite_timestamp(last_used_str)
                    now_dt = datetime.now(timezone.utc)
                    elapsed_seconds = (now_dt - last_used_dt).total_seconds()
                    if elapsed_seconds < COOLDOWN_SECONDS:
                        remaining = int(COOLDOWN_SECONDS - elapsed_seconds)
                        await update.message.reply_text(
                            f"Ещё рано. Повтори через {_format_remaining(remaining)} (кд {COOLDOWN_SECONDS // 3600} ч)"
                        )
                        return
                except Exception as e:
                    logger.warning(f"Не удалось разобрать время последнего использования /tits: {e}")

        # Генерируем изменение размера
        change = self.game_logic.calculate_size_change()
        new_size, actual_change = self.game_logic.apply_size_change(
            user_data['breast_size'], change
        )
        
        # Обновляем размер в базе
        self.db.update_breast_size(user.id, new_size, actual_change, chat.id)
        
        # Формируем сообщение
        user_name = user.first_name or user.username or f"Пользователь {user.id}"
        
        # Рофельный, но аккуратный текст без эмодзи
        verb = "прибавила" if actual_change > 0 else "убавила"
        delta_word = "размеров" if abs(actual_change) != 1 else "размер"
        rank = self.db.get_user_rank(user.id)
        rank_line = f"Твоё место в топе: {rank}" if rank else "В топ пока не попал"
        message = (
            f"{user_name}, твоя грудь {verb} на {abs(actual_change)} {delta_word}\n"
            f"Текущее значение: {new_size}\n"
            f"{rank_line}"
        )
        
        await update.message.reply_text(message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        user = update.effective_user
        
        # Получаем статистику пользователя
        stats = self.db.get_user_stats(user.id)
        
        if not stats:
            await update.message.reply_text("Статистика не найдена. Попробуйте использовать /tits сначала!")
            return
        
        user_name = user.first_name or user.username or f"Пользователь {user.id}"
        
        message = (
            f"📊 Статистика {user_name}:\n\n"
            f"🍒 Текущий размер: {stats['breast_size']} "
            f"({self.game_logic.get_size_description(stats['breast_size'])}) "
            f"{self.game_logic.get_emoji_for_size(stats['breast_size'])}\n\n"
            f"📈 Всего изменений: {stats['total_changes']}\n"
            f"📅 Первое изменение: {stats['first_change'] or 'Нет данных'}\n"
            f"🕐 Последнее изменение: {stats['last_change'] or 'Нет данных'}\n\n"
            f"Используйте /history для просмотра истории изменений"
        )
        
        await update.message.reply_text(message)
    
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /top"""
        # Получаем топ пользователей
        top_users = self.db.get_top_users(10)
        
        if not top_users:
            await update.message.reply_text("Пока нет данных для топ-листа. Попробуйте использовать /tits!")
            return
        
        message = "🏆 Топ-10 пользователей по размеру груди:\n\n"
        
        for i, user in enumerate(top_users, 1):
            user_name = user['first_name'] or user['username'] or f"Пользователь {user['user_id']}"
            size_desc = self.game_logic.get_size_description(user['breast_size'])
            emoji = self.game_logic.get_emoji_for_size(user['breast_size'])
            
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            message += f"{medal} {user_name}: {user['breast_size']} ({size_desc}) {emoji}\n"
        
        await update.message.reply_text(message)
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /history"""
        user = update.effective_user
        
        # Получаем историю изменений
        history = self.db.get_user_history(user.id, 5)
        
        if not history:
            await update.message.reply_text("История изменений не найдена. Попробуйте использовать /tits сначала!")
            return
        
        user_name = user.first_name or user.username or f"Пользователь {user.id}"
        
        message = f"📜 История изменений {user_name}:\n\n"
        
        for i, record in enumerate(history, 1):
            change_desc = self.game_logic.get_change_description(record['change_amount'])
            emoji = self.game_logic.get_emoji_for_change(record['change_amount'])
            chat_title = record['chat_title'] or "Неизвестный чат"
            
            message += (
                f"{i}. {emoji} {change_desc}\n"
                f"   Было: {record['old_size']} → Стало: {record['new_size']}\n"
                f"   Чат: {chat_title}\n"
                f"   Дата: {record['created_at']}\n\n"
            )
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = (
            "Короткая справка:\n"
            "/tits — изменить размер (−10…+10)\n"
            "/stats — твой текущий размер\n"
            "/top — таблица лидеров\n"
            "/history — последние изменения\n"
            "/help — эта справка"
        )
        
        await update.message.reply_text(help_message)
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик неизвестных команд"""
        await update.message.reply_text(
            "❓ Неизвестная команда. Используйте /help для просмотра доступных команд"
        )

    async def reset_all_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Админ-команда: сбросить всю статистику у всех пользователей."""
        user = update.effective_user
        if user.id not in ADMIN_USER_IDS:
            await update.message.reply_text("⛔ У вас нет прав для этой команды")
            return
        try:
            self.db.reset_all_stats()
            await update.message.reply_text("✅ Вся статистика сброшена")
        except Exception as e:
            logger.exception("Ошибка при сбросе статистики")
            await update.message.reply_text("⚠️ Не удалось выполнить сброс. Проверьте логи")
