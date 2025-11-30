# Quick Start Guide

Быстрое руководство по запуску проекта.

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 2: Генерация gRPC кода

```bash
make proto
```

## Шаг 3: Настройка окружения

Скопируйте `.env.example` в `.env` и заполните необходимые значения:

```bash
cp .env.example .env
# Отредактируйте .env файл
```

## Шаг 4: Инициализация DVC (опционально)

```bash
bash setup_dvc.sh
```

## Шаг 5: Запуск ClearML (опционально)

```bash
docker-compose up -d
```

После запуска создайте аккаунт на http://localhost:8080 и получите API ключи.

## Шаг 6: Запуск сервисов

### Вариант A: Локальный запуск

**Терминал 1 - REST API:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Терминал 2 - gRPC сервер:**
```bash
python app/grpc_server/server.py
```

**Терминал 3 - Dashboard:**
```bash
streamlit run dashboard/main.py
```

### Вариант B: Запуск в Minikube

```bash
make deploy
```

После развертывания получите URL:
```bash
minikube service mlops-api -n mlops --url
minikube service mlops-dashboard -n mlops --url
```

## Шаг 7: Тестирование

### REST API

Откройте в браузере: http://localhost:8000/docs

### gRPC

```bash
python grpc_client/client.py
```

### Dashboard

Откройте в браузере: http://localhost:8501

## Пример использования

1. Загрузите датасет через дашборд или API
2. Обучите модель через дашборд или API
3. Получите предсказания через дашборд или API

## Полезные команды

```bash
# Просмотр логов
make logs

# Остановка Minikube
make minikube-stop

# Удаление из Minikube
make undeploy

# Очистка
make clean
```

