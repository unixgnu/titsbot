import random
from typing import Tuple
from config import MIN_SIZE, MAX_SIZE, MIN_CHANGE, MAX_CHANGE, POSITIVE_PROBABILITY

class GameLogic:
    @staticmethod
    def calculate_size_change() -> int:
        """
        Генерирует случайное изменение размера груди
        Возвращает равновероятное целое число от MIN_CHANGE до MAX_CHANGE, исключая 0
        """
        # Формируем список положительных и отрицательных изменений, исключая 0
        negatives = [v for v in range(MIN_CHANGE, 0)]
        positives = [v for v in range(1, MAX_CHANGE + 1)]

        # Выбираем знак в зависимости от вероятности POSITIVE_PROBABILITY
        if random.random() < POSITIVE_PROBABILITY:
            return random.choice(positives)
        else:
            return random.choice(negatives)
    
    @staticmethod
    def apply_size_change(current_size: int, change: int) -> Tuple[int, int]:
        """
        Применяет изменение к текущему размеру груди
        Возвращает (новый_размер, фактическое_изменение)
        """
        new_size = current_size + change
        
        # Ограничиваем размер в заданных пределах
        if new_size < MIN_SIZE:
            actual_change = MIN_SIZE - current_size
            new_size = MIN_SIZE
        elif new_size > MAX_SIZE:
            actual_change = MAX_SIZE - current_size
            new_size = MAX_SIZE
        else:
            actual_change = change
        
        return new_size, actual_change
    
    @staticmethod
    def get_size_description(size: int) -> str:
        """
        Возвращает описание размера груди
        """
        if size <= -80:
            return "плоская как доска"
        elif size <= -60:
            return "очень маленькая"
        elif size <= -40:
            return "маленькая"
        elif size <= -20:
            return "небольшая"
        elif size <= 0:
            return "средняя"
        elif size <= 20:
            return "хорошая"
        elif size <= 40:
            return "большая"
        elif size <= 60:
            return "очень большая"
        elif size <= 80:
            return "огромная"
        else:
            return "невероятно огромная"
    
    @staticmethod
    def get_change_description(change: int) -> str:
        """
        Возвращает описание изменения размера
        """
        if change > 0:
            if change >= 8:
                return f"выросла на {change} размеров! 🎉"
            elif change >= 5:
                return f"выросла на {change} размеров! 😊"
            elif change >= 2:
                return f"выросла на {change} размера 🙂"
            else:
                return f"выросла на {change} размер 😌"
        else:
            change_abs = abs(change)
            if change_abs >= 8:
                return f"уменьшилась на {change_abs} размеров! 😱"
            elif change_abs >= 5:
                return f"уменьшилась на {change_abs} размеров! 😢"
            elif change_abs >= 2:
                return f"уменьшилась на {change_abs} размера 😕"
            else:
                return f"уменьшилась на {change_abs} размер 😔"
    
    @staticmethod
    def get_emoji_for_size(size: int) -> str:
        """
        Возвращает эмодзи для размера груди
        """
        if size <= -60:
            return "🫤"
        elif size <= -20:
            return "😐"
        elif size <= 20:
            return "😊"
        elif size <= 60:
            return "😍"
        else:
            return "🤩"
    
    @staticmethod
    def get_emoji_for_change(change: int) -> str:
        """
        Возвращает эмодзи для изменения размера
        """
        if change > 0:
            if change >= 8:
                return "🎉"
            elif change >= 5:
                return "😊"
            elif change >= 2:
                return "🙂"
            else:
                return "😌"
        else:
            change_abs = abs(change)
            if change_abs >= 8:
                return "😱"
            elif change_abs >= 5:
                return "😢"
            elif change_abs >= 2:
                return "😕"
            else:
                return "😔"
