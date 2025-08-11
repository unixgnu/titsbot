@echo off
echo Starting TitsBot...
echo.

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Запускаем бота
python main.py

REM Пауза для просмотра ошибок
pause
