import sqlite3
import logging
from typing import Optional, List, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Создает соединение с базой данных"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Инициализирует базу данных и создает необходимые таблицы"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Создаем таблицу пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    breast_size INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицу чатов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    chat_type TEXT,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Создаем таблицу истории изменений
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS size_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    chat_id INTEGER,
                    old_size INTEGER,
                    new_size INTEGER,
                    change_amount INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                )
            ''')
            
            conn.commit()
            logger.info("База данных инициализирована")

    def reset_all_stats(self):
        """Полный сброс: очистить историю и пользователей, чтобы топ стал пустым."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Сначала чистим историю изменений
            cursor.execute('DELETE FROM size_history')
            # Затем удаляем всех пользователей (топ станет пустым)
            cursor.execute('DELETE FROM users')
            # По желанию можно также очистить чаты. Оставим чаты, чтобы названия сохранялись.
            conn.commit()
    
    def get_or_create_user(self, user_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> dict:
        """Получает или создает пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, breast_size, created_at, updated_at
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                # Обновляем информацию о пользователе
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, first_name = ?, last_name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (username, first_name, last_name, user_id))
                
                return {
                    'user_id': user[0],
                    'username': username or user[1],
                    'first_name': first_name or user[2],
                    'last_name': last_name or user[3],
                    'breast_size': user[4],
                    'created_at': user[5],
                    'updated_at': user[6]
                }
            else:
                # Создаем нового пользователя
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name, breast_size)
                    VALUES (?, ?, ?, ?, 0)
                ''', (user_id, username, first_name, last_name))
                
                return {
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'breast_size': 0,
                    'created_at': None,
                    'updated_at': None
                }
    
    def get_or_create_chat(self, chat_id: int, chat_type: str, title: str = None) -> dict:
        """Получает или создает чат"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Проверяем, существует ли чат
            cursor.execute('''
                SELECT chat_id, chat_type, title, created_at
                FROM chats WHERE chat_id = ?
            ''', (chat_id,))
            
            chat = cursor.fetchone()
            
            if chat:
                return {
                    'chat_id': chat[0],
                    'chat_type': chat[1],
                    'title': chat[2],
                    'created_at': chat[3]
                }
            else:
                # Создаем новый чат
                cursor.execute('''
                    INSERT INTO chats (chat_id, chat_type, title)
                    VALUES (?, ?, ?)
                ''', (chat_id, chat_type, title))
                
                return {
                    'chat_id': chat_id,
                    'chat_type': chat_type,
                    'title': title,
                    'created_at': None
                }
    
    def update_breast_size(self, user_id: int, new_size: int, change_amount: int, chat_id: int):
        """Обновляет размер груди пользователя и сохраняет историю"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем текущий размер
            cursor.execute('SELECT breast_size FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            if result:
                old_size = result[0]
                
                # Обновляем размер груди
                cursor.execute('''
                    UPDATE users 
                    SET breast_size = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (new_size, user_id))
                
                # Сохраняем в историю
                cursor.execute('''
                    INSERT INTO size_history (user_id, chat_id, old_size, new_size, change_amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, chat_id, old_size, new_size, change_amount))
                
                conn.commit()
                return True
            else:
                return False

    def get_last_tits_usage(self, user_id: int) -> Optional[str]:
        """Возвращает время последнего использования /tits пользователем (строка TIMESTAMP)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT MAX(created_at)
                FROM size_history
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
            return None
    
    def get_user_stats(self, user_id: int) -> Optional[dict]:
        """Получает статистику пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT u.user_id, u.username, u.first_name, u.last_name, 
                       u.breast_size, u.created_at,
                       COUNT(h.id) as total_changes,
                       MIN(h.created_at) as first_change,
                       MAX(h.created_at) as last_change
                FROM users u
                LEFT JOIN size_history h ON u.user_id = h.user_id
                WHERE u.user_id = ?
                GROUP BY u.user_id
            ''', (user_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'user_id': result[0],
                    'username': result[1],
                    'first_name': result[2],
                    'last_name': result[3],
                    'breast_size': result[4],
                    'created_at': result[5],
                    'total_changes': result[6],
                    'first_change': result[7],
                    'last_change': result[8]
                }
            return None
    
    def get_top_users(self, limit: int = 10) -> List[dict]:
        """Получает топ пользователей по размеру груди"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, username, first_name, last_name, breast_size
                FROM users
                ORDER BY breast_size DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            
            return [
                {
                    'user_id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'breast_size': row[4]
                }
                for row in results
            ]

    def get_user_rank(self, user_id: int) -> Optional[int]:
        """Возвращает место пользователя в рейтинге (1 = лучший)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Получаем текущий размер
            cursor.execute('SELECT breast_size FROM users WHERE user_id = ?', (user_id,))
            res = cursor.fetchone()
            if not res:
                return None
            size = res[0]
            # Количество пользователей с бОльшим размером + 1 = ранг
            cursor.execute('SELECT COUNT(*) FROM users WHERE breast_size > ?', (size,))
            higher = cursor.fetchone()[0]
            return higher + 1
    
    def get_user_history(self, user_id: int, limit: int = 10) -> List[dict]:
        """Получает историю изменений пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT h.old_size, h.new_size, h.change_amount, h.created_at,
                       c.title as chat_title
                FROM size_history h
                LEFT JOIN chats c ON h.chat_id = c.chat_id
                WHERE h.user_id = ?
                ORDER BY h.created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            
            return [
                {
                    'old_size': row[0],
                    'new_size': row[1],
                    'change_amount': row[2],
                    'created_at': row[3],
                    'chat_title': row[4]
                }
                for row in results
            ]
