#!/usr/bin/env python3
"""
Скрипт для тестирования базы данных TitsBot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from game_logic import GameLogic

def test_database():
    """Тестирует функциональность базы данных"""
    print("🧪 Тестирование базы данных TitsBot...")
    
    # Инициализируем базу данных
    db = Database("test_titsbot.db")
    game_logic = GameLogic()
    
    try:
        # Тест 1: Создание пользователя
        print("\n1. Тест создания пользователя...")
        user = db.get_or_create_user(
            user_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        print(f"✅ Пользователь создан: {user}")
        
        # Тест 2: Создание чата
        print("\n2. Тест создания чата...")
        chat = db.get_or_create_chat(
            chat_id=67890,
            chat_type="group",
            title="Test Chat"
        )
        print(f"✅ Чат создан: {chat}")
        
        # Тест 3: Обновление размера груди
        print("\n3. Тест обновления размера груди...")
        change = game_logic.calculate_size_change()
        new_size, actual_change = game_logic.apply_size_change(user['breast_size'], change)
        
        success = db.update_breast_size(12345, new_size, actual_change, 67890)
        print(f"✅ Размер обновлен: {success}")
        print(f"   Изменение: {change}, Фактическое: {actual_change}, Новый размер: {new_size}")
        
        # Тест 4: Получение статистики
        print("\n4. Тест получения статистики...")
        stats = db.get_user_stats(12345)
        print(f"✅ Статистика получена: {stats}")
        
        # Тест 5: Получение истории
        print("\n5. Тест получения истории...")
        history = db.get_user_history(12345, 5)
        print(f"✅ История получена: {len(history)} записей")
        for record in history:
            print(f"   {record}")
        
        # Тест 6: Получение топ пользователей
        print("\n6. Тест получения топ пользователей...")
        top_users = db.get_top_users(5)
        print(f"✅ Топ пользователей получен: {len(top_users)} пользователей")
        for user in top_users:
            print(f"   {user}")
        
        # Тест 7: Еще несколько изменений для разнообразия
        print("\n7. Тест множественных изменений...")
        for i in range(3):
            change = game_logic.calculate_size_change()
            current_size = db.get_user_stats(12345)['breast_size']
            new_size, actual_change = game_logic.apply_size_change(current_size, change)
            db.update_breast_size(12345, new_size, actual_change, 67890)
            print(f"   Изменение {i+1}: {change} → {actual_change}, Размер: {new_size}")
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False
    
    finally:
        # Удаляем тестовую базу данных
        try:
            os.remove("test_titsbot.db")
            print("\n🧹 Тестовая база данных удалена")
        except:
            pass
    
    return True

def test_game_logic():
    """Тестирует игровую логику"""
    print("\n🎮 Тестирование игровой логики...")
    
    game_logic = GameLogic()
    
    try:
        # Тест генерации изменений
        print("1. Тест генерации изменений...")
        changes = []
        for _ in range(100):
            change = game_logic.calculate_size_change()
            changes.append(change)
            if change == 0:
                print("❌ Обнаружено изменение равное 0!")
                return False
        
        print(f"✅ Сгенерировано {len(changes)} изменений")
        print(f"   Минимальное: {min(changes)}, Максимальное: {max(changes)}")
        
        # Тест применения изменений
        print("\n2. Тест применения изменений...")
        test_sizes = [-100, -50, 0, 50, 100]
        for size in test_sizes:
            change = game_logic.calculate_size_change()
            new_size, actual_change = game_logic.apply_size_change(size, change)
            print(f"   Размер {size} + {change} = {new_size} (фактическое изменение: {actual_change})")
        
        # Тест описаний
        print("\n3. Тест описаний...")
        test_sizes = [-90, -60, -30, 0, 30, 60, 90]
        for size in test_sizes:
            desc = game_logic.get_size_description(size)
            emoji = game_logic.get_emoji_for_size(size)
            print(f"   Размер {size}: {desc} {emoji}")
        
        print("\n🎉 Тесты игровой логики прошли успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании игровой логики: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов TitsBot...")
    
    db_success = test_database()
    game_success = test_game_logic()
    
    if db_success and game_success:
        print("\n✅ Все тесты прошли успешно!")
        sys.exit(0)
    else:
        print("\n❌ Некоторые тесты не прошли!")
        sys.exit(1)
