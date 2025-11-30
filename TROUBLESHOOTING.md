# Решение проблем

## Проблема: Ошибка компиляции scikit-learn

**Ошибка:**
```
Cython.Compiler.Errors.CompileError: sklearn\linear_model\_cd_fast.pyx
```

**Причина:** scikit-learn 1.3.2 не совместим с Python 3.14

**Решение:**
1. Обновите scikit-learn до версии 1.5.0 или выше:
```bash
pip install --upgrade scikit-learn>=1.5.0
```

2. Или используйте Python 3.11 или 3.12 (рекомендуется):
```bash
# Создайте виртуальное окружение с Python 3.11
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

## Проблема: ModuleNotFoundError: No module named 'grpc_tools'

**Ошибка:**
```
ModuleNotFoundError: No module named 'grpc_tools'
```

**Решение:**
Установите зависимости:
```bash
pip install -r requirements.txt
```

Или установите grpc-tools отдельно:
```bash
pip install grpcio-tools
```

## Проблема: minikube не найден

**Ошибка:**
```
process_begin: CreateProcess(NULL, minikube start --driver=docker, ...) failed.
```

**Решение:**

### Windows:
1. Скачайте Minikube: https://minikube.sigs.k8s.io/docs/start/
2. Или используйте Chocolatey:
```powershell
choco install minikube
```

3. Или используйте winget:
```powershell
winget install Kubernetes.minikube
```

4. Добавьте minikube в PATH

### Альтернатива: Запуск без Minikube

Для локального запуска Minikube не обязателен:
```bash
# Запустите только REST API и Dashboard локально
uvicorn app.main:app --host 0.0.0.0 --port 8000
streamlit run dashboard/main.py
```

## Проблема: uvicorn не найден

**Ошибка:**
```
uvicorn : Имя "uvicorn" не распознано
```

**Решение:**
1. Убедитесь, что виртуальное окружение активировано
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Или установите uvicorn отдельно:
```bash
pip install uvicorn[standard]
```

## Проблема: Ошибки при установке зависимостей

**Решение:**
1. Обновите pip:
```bash
python -m pip install --upgrade pip
```

2. Установите зависимости по частям:
```bash
# Сначала базовые
pip install fastapi uvicorn pydantic

# Затем gRPC
pip install grpcio grpcio-tools protobuf

# Затем ML библиотеки
pip install scikit-learn numpy pandas joblib

# И так далее...
```

3. Для Windows может потребоваться Visual C++ Build Tools для компиляции некоторых пакетов

## Проблема: Python 3.14 слишком новый

**Решение:**
Используйте Python 3.11 или 3.12 (рекомендуется):
```bash
# Создайте виртуальное окружение
python3.11 -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установите зависимости
pip install -r requirements.txt
```

## Быстрая проверка установки

```bash
# Проверьте Python
python --version  # Должно быть 3.9-3.12

# Проверьте установленные пакеты
pip list | grep -E "(fastapi|grpc|scikit|streamlit)"

# Проверьте gRPC
python -c "import grpc; print('OK')"

# Проверьте FastAPI
python -c "import fastapi; print('OK')"
```

## Альтернативный способ запуска (без Minikube)

Если Minikube вызывает проблемы, можно запустить локально:

1. **REST API:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. **gRPC сервер:**
```bash
python app/grpc_server/server.py
```

3. **Dashboard:**
```bash
streamlit run dashboard/main.py
```

4. **ClearML (опционально):**
```bash
docker-compose up -d
```

5. **MinIO (опционально, можно запустить локально):**
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  minio/minio server /data --console-address ":9001"
```


