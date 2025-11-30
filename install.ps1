# PowerShell скрипт для установки зависимостей на Windows

Write-Host "MLOps Homework 1 - Установка зависимостей" -ForegroundColor Green

# Проверка Python
Write-Host "`nПроверка Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ОШИБКА: Python не найден! Установите Python 3.9-3.12" -ForegroundColor Red
    exit 1
}
Write-Host "Найден: $pythonVersion" -ForegroundColor Green

# Обновление pip
Write-Host "`nОбновление pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Создание виртуального окружения (опционально)
$createVenv = Read-Host "`nСоздать виртуальное окружение? (y/n)"
if ($createVenv -eq "y" -or $createVenv -eq "Y") {
    Write-Host "Создание виртуального окружения..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "Активация виртуального окружения..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "Виртуальное окружение активировано!" -ForegroundColor Green
}

# Установка зависимостей
Write-Host "`nУстановка зависимостей из requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ Все зависимости установлены успешно!" -ForegroundColor Green
    Write-Host "`nСледующие шаги:" -ForegroundColor Cyan
    Write-Host "1. Сгенерируйте gRPC код: python -m grpc_tools.protoc -I app/grpc_server --python_out=app/grpc_server --grpc_python_out=app/grpc_server app/grpc_server/mlops.proto"
    Write-Host "2. Запустите REST API: uvicorn app.main:app --host 0.0.0.0 --port 8000"
    Write-Host "3. Запустите gRPC сервер: python app/grpc_server/server.py"
    Write-Host "4. Запустите Dashboard: streamlit run dashboard/main.py"
} else {
    Write-Host "`n✗ Ошибка при установке зависимостей!" -ForegroundColor Red
    Write-Host "Проверьте TROUBLESHOOTING.md для решения проблем" -ForegroundColor Yellow
    exit 1
}


