# MLOps Homework 1

Система для обучения, управления и использования ML-моделей с поддержкой REST и gRPC API, интерактивным дашбордом и интеграцией с DVC и ClearML.

## Архитектура

- **REST API** (FastAPI) - основной сервис для работы с моделями
- **gRPC API** - альтернативный интерфейс для работы с моделями
- **Streamlit Dashboard** - интерактивный веб-интерфейс
- **DVC** - версионирование датасетов
- **ClearML** - отслеживание экспериментов и управление моделями
- **MinIO** - S3-совместимое хранилище для весов и кэша
- **Kubernetes (Minikube)** - оркестрация сервисов

## Структура проекта

```
.
├── app/                    # Основное приложение
│   ├── api/               # REST API эндпоинты
│   ├── grpc_server/       # gRPC сервер
│   ├── models/            # ML модели
│   ├── services/          # Бизнес-логика
│   └── utils/             # Утилиты
├── dashboard/             # Streamlit дашборд
├── k8s/                   # Kubernetes манифесты
├── docker-compose.yml     # Docker Compose для ClearML
├── Dockerfile             # Docker образ для сервиса
├── Makefile              # Команды для запуска
└── requirements.txt      # Зависимости Python
```

## Быстрый старт

### Предварительные требования

- Docker (для Minikube и ClearML)
- Minikube (опционально, для развертывания в Kubernetes)
- kubectl (опционально, для работы с Minikube)
- Make (опционально, для удобства запуска)
- Python 3.9-3.12 (рекомендуется 3.11 или 3.12, Python 3.14 может иметь проблемы совместимости)

**Примечание:** Для локального запуска Minikube не обязателен. См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) для решения проблем.

### Локальный запуск (без Kubernetes)

1. Создайте необходимые директории:

**Windows (PowerShell):**
```powershell
# Вариант 1: Используйте скрипт
.\create_dirs.ps1

# Вариант 2: Вручную
New-Item -ItemType Directory -Force -Path app/models, app/data, models, data
```

**Linux/Mac (Bash):**
```bash
mkdir -p app/models app/data models data
```

2. Установите зависимости:
```bash
# Обновите pip
python -m pip install --upgrade pip

# Установите зависимости
pip install -r requirements.txt
```

**Примечание:** Если возникают проблемы с установкой scikit-learn на Python 3.14, используйте Python 3.11 или 3.12. См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

3. Настройте переменные окружения (создайте `.env` файл):
```env
CLEARML_API_ACCESS_KEY=your_key
CLEARML_API_SECRET_KEY=your_secret
CLEARML_WEB_HOST=http://localhost:8080
CLEARML_API_HOST=http://localhost:8008
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

3. Сгенерируйте gRPC код из proto файла:
```bash
make proto
# или вручную:
python -m grpc_tools.protoc -I app/grpc_server --python_out=app/grpc_server --grpc_python_out=app/grpc_server app/grpc_server/mlops.proto
```

4. Инициализируйте DVC (опционально):
```bash
bash setup_dvc.sh
```

5. Запустите сервисы:
```bash
# Запуск REST API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Запуск gRPC сервера (в отдельном терминале)
python app/grpc_server/server.py

# Запуск дашборда (в отдельном терминале)
streamlit run dashboard/main.py
```

### Запуск в Minikube

1. Запустите Minikube:
```bash
minikube start --driver=docker
```

2. Используйте Makefile для автоматического развертывания:
```bash
make deploy
```

Это команда:
- Создаст необходимые Kubernetes ресурсы
- Развернет MinIO
- Развернет REST API сервис
- Развернет Streamlit дашборд
- Настроит персистентные тома

3. Для доступа к сервисам:
```bash
# Получить URL для REST API
minikube service mlops-api --url

# Получить URL для дашборда
minikube service mlops-dashboard --url
```

### Запуск ClearML

ClearML можно запустить отдельно через Docker Compose:

```bash
docker-compose up -d
```

ClearML будет доступен по адресу `http://localhost:8080`

## API Документация

### REST API

После запуска сервиса:
- **Корневой путь**: `http://localhost:8000/` — информация об API и ссылки на документацию
- **Swagger UI**: `http://localhost:8000/docs` — интерактивная документация
- **ReDoc**: `http://localhost:8000/redoc` — альтернативная документация

#### Основные эндпоинты:

- `GET /health` - проверка статуса сервиса
- `GET /models/available` - список доступных классов моделей
- `GET /models` - список обученных моделей
- `POST /models/train` - обучение модели
- `POST /models/{model_id}/predict` - получение предсказания
- `POST /models/{model_id}/retrain` - переобучение модели
- `DELETE /models/{model_id}` - удаление модели
- `GET /datasets` - список датасетов
- `POST /datasets/upload` - загрузка датасета

### gRPC API

gRPC сервер запускается на порту 50051. 

**Запуск gRPC сервера:**
```bash
python app/grpc_server/server.py
```

**Тестирование gRPC сервиса:**

Используйте Python скрипт:
```bash
python grpc_client/client.py [server_address]
# По умолчанию: python grpc_client/client.py localhost:50051
```

Или используйте Jupyter ноутбук:
```bash
jupyter notebook grpc_client/client.ipynb
```

**Важно:** Перед запуском gRPC сервера убедитесь, что сгенерированы Python файлы из proto:
```bash
make proto
```

## Использование дашборда

Дашборд доступен по адресу `http://localhost:8501` и содержит три вкладки:

1. **Датасеты** - просмотр, загрузка и удаление датасетов из DVC
2. **Обучение** - обучение моделей с настройкой гиперпараметров (JSON)
3. **Инференс** - получение предсказаний от обученных моделей

## Работа с DVC

Датасеты версионируются через DVC. Для работы с датасетами:

```bash
# Автоматическая настройка (использует setup_dvc.sh)
bash setup_dvc.sh

# Или вручную:
# Инициализация DVC
dvc init

# Добавление удаленного хранилища (MinIO)
dvc remote add -d minio s3://dvc-data \
    --endpoint-url http://localhost:9000 \
    --access-key-id minioadmin \
    --secret-access-key minioadmin

# Добавление датасета
dvc add app/data/dataset.csv
git add app/data/dataset.csv.dvc

# Загрузка в S3/MinIO
dvc push

# Загрузка датасета из S3/MinIO
dvc pull
```

**Примечание:** В Minikube MinIO доступен по адресу `minio:9000` внутри кластера.

## Работа с ClearML

Каждое обучение модели создает отдельный эксперимент в ClearML, а модель сохраняется в ClearML Model Registry.

**Запуск ClearML:**

```bash
docker-compose up -d
```

ClearML будет доступен по адресу `http://localhost:8080`

**Настройка ClearML:**

1. Запустите ClearML сервер через docker-compose
2. Создайте аккаунт на `http://localhost:8080` (первый пользователь становится администратором)
3. Получите API ключи в настройках профиля (Settings -> Workspace -> Create new credentials)
4. Добавьте ключи в `.env` файл:
```env
CLEARML_API_ACCESS_KEY=your_access_key
CLEARML_API_SECRET_KEY=your_secret_key
CLEARML_WEB_HOST=http://localhost:8080
CLEARML_API_HOST=http://localhost:8008
```

**Примечание:** ClearML можно также развернуть в Minikube, но для упрощения рекомендуется использовать docker-compose.

## Makefile команды

- `make deploy` - развернуть все в Minikube (включает сборку образов)
- `make undeploy` - удалить все из Minikube
- `make build` - собрать Docker образы и загрузить в Minikube
- `make proto` - сгенерировать gRPC код из proto файла
- `make logs` - посмотреть логи сервисов
- `make clean` - очистить временные файлы
- `make minikube-start` - запустить Minikube
- `make minikube-stop` - остановить Minikube

## Разработка

### Структура кода

- `app/main.py` - точка входа FastAPI приложения
- `app/api/` - REST API эндпоинты
- `app/grpc_server/` - gRPC сервер и proto файлы
- `app/models/` - классы ML моделей
- `app/services/` - сервисы для работы с моделями, DVC, ClearML
- `dashboard/main.py` - Streamlit дашборд

### Добавление новой модели

1. Создайте класс модели в `app/models/` наследуя от `BaseModel`
2. Реализуйте методы `train()`, `predict()`, `get_hyperparameters()`
3. Зарегистрируйте модель в `app/models/__init__.py` в словаре `MODEL_REGISTRY`

### Пример добавления модели

```python
# app/models/my_model.py
from app.models.base_model import BaseModel

class MyModel(BaseModel):
    def train(self, X, y):
        # Реализация обучения
        pass
    
    def predict(self, X):
        # Реализация предсказания
        pass

# app/models/__init__.py
from app.models.my_model import MyModel

MODEL_REGISTRY = {
    'random_forest': RandomForestModel,
    'logistic_regression': LogisticRegressionModel,
    'my_model': MyModel  # Добавить здесь
}
```

## Логгирование

Все важные действия логгируются через стандартный Python logger. Логи доступны в консоли и могут быть перенаправлены в файл.

## Лицензия

MIT

