#!/bin/bash

cd "$(dirname "$0")"

echo "🚀 Активация виртуального окружения..."
source .venv/bin/activate

echo "🧠 Запуск сервера с подавлением ошибок OpenMP..."
KMP_DUPLICATE_LIB_OK=TRUE uvicorn app:app --reload
