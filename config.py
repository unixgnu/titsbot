import os
from dotenv import load_dotenv
from typing import Set

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Читаем токен из переменных окружения / .env
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден. Укажите его в .env или в переменных окружения")

# Настройки базы данных
DATABASE_PATH = os.getenv('DATABASE_PATH', 'titsbot.db')

# Настройки игры
MIN_SIZE = -1000000  # Минимальный размер груди
MAX_SIZE = 1000000   # Максимальный размер груди
MIN_CHANGE = -10 # Минимальное изменение за раз
MAX_CHANGE = 10  # Максимальное изменение за раз

# Ограничение частоты использования команды /tits
# ENFORCE_COOLDOWN: включить/выключить ограничение (по умолчанию включено, чтобы не спамили)
# COOLDOWN_SECONDS: интервал в секундах (по умолчанию 24 часа)
ENFORCE_COOLDOWN = os.getenv('ENFORCE_COOLDOWN', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
COOLDOWN_SECONDS = int(os.getenv('COOLDOWN_SECONDS', str(12 * 60 * 60)))

# Параметр удачи: число от -100 до 100
# -100 = всегда в минус, 0 = честные 50/50, 100 = всегда в плюс
try:
    LUCK = int(os.getenv('LUCK', '37'))
except ValueError:
    LUCK = 0

if LUCK < -100:
    LUCK = -100
elif LUCK > 100:
    LUCK = 100

# Вероятность положительного изменения на основе удачи
POSITIVE_PROBABILITY = max(0.0, min(1.0, 0.5 + (LUCK / 200.0)))

# Администраторы бота: список Telegram user_id, имеющих доступ к /reset_all
def _parse_admin_ids(raw_value: str) -> Set[int]:
    ids: Set[int] = set()
    if not raw_value:
        return ids
    for piece in raw_value.replace(';', ',').split(','):
        piece = piece.strip()
        if not piece:
            continue
        try:
            ids.add(int(piece))
        except ValueError:
            continue
    return ids

# Укажите свои ID через переменную окружения ADMIN_USER_IDS="123,456" или отредактируйте список ниже
ADMIN_USER_IDS: Set[int] = _parse_admin_ids(os.getenv('ADMIN_USER_IDS', '1855337325'))
# Прямая настройка (на случай отсутствия переменных окружения):
# ADMIN_USER_IDS: Set[int] = {123456789}

