Write-Host "Starting TitsBot..." -ForegroundColor Green
Write-Host ""

# Активируем виртуальное окружение
& ".\venv\Scripts\Activate.ps1"

# Запускаем бота
python main.py

# Пауза для просмотра ошибок
Read-Host "Press Enter to exit"
