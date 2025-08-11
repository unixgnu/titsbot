# TitsBot - Telegram бот для отслеживания размера груди

Забавный Telegram бот, который позволяет пользователям изменять свой "размер груди" случайным образом и отслеживать статистику.

## Функциональность

- 🍒 Команда `/tits` - случайно изменяет размер груди (-10 до +10, 0 не выпадает)
- 📊 Команда `/stats` - показывает статистику пользователя
- 🏆 Команда `/top` - показывает топ-10 пользователей
- 📜 Команда `/history` - показывает историю изменений
- 💾 Хранение всех данных в SQLite базе данных
- 🎮 Поддержка групповых чатов

## Установка и настройка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd titsbot
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
```

### 3. Активация виртуального окружения

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Создание бота в Telegram
1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 4. Настройка конфигурации
1. Скопируйте `env_example.txt` в `.env`
2. Замените `your_bot_token_here` на ваш токен бота

```bash
cp env_example.txt .env
# Отредактируйте .env файл
```

### 5. Запуск бота
```bash
python main.py
```

## Структура проекта

```
titsbot/
├── main.py              # Основной файл бота
├── config.py            # Конфигурация
├── database.py          # Работа с базой данных
├── game_logic.py        # Игровая логика
├── handlers.py          # Обработчики команд
├── requirements.txt     # Зависимости
├── env_example.txt      # Пример конфигурации
└── README.md           # Документация
```

## Команды бота

- `/start` - Запуск бота и приветствие
- `/tits` - Изменить размер груди случайным образом
- `/stats` - Показать свою статистику
- `/top` - Показать топ-10 пользователей
- `/history` - Показать историю изменений
- `/help` - Показать справку

## База данных

Бот использует SQLite для хранения данных. Создаются следующие таблицы:

- `users` - информация о пользователях
- `chats` - информация о чатах
- `size_history` - история изменений размера

## Настройки

В файле `config.py` можно изменить:

- `MIN_SIZE` / `MAX_SIZE` - пределы размера груди (-100 до +100)
- `MIN_CHANGE` / `MAX_CHANGE` - пределы изменения за раз (-10 до +10)

## Развертывание

### Локально
```bash
python main.py
```

### На сервере
Рекомендуется использовать systemd или supervisor для автозапуска:

```bash
# Создайте systemd сервис
sudo nano /etc/systemd/system/titsbot.service
```

```ini
[Unit]
Description=TitsBot Telegram Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/titsbot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable titsbot
sudo systemctl start titsbot
```

## Логирование

Бот ведет логи в формате:
```
2024-01-01 12:00:00,000 - main - INFO - Бот запускается...
```

## Безопасность

- Токен бота хранится в переменных окружения
- База данных защищена от SQL-инъекций через параметризованные запросы
- Обработка ошибок предотвращает падение бота

## Лицензия

MIT License

## Поддержка

При возникновении проблем создайте issue в репозитории.
