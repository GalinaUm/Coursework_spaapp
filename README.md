# DRF Project

## 📌 Описание проекта

Backend-приложение на Django REST Framework.

Реализовано:
- работа с пользователями
- работа с материалами
- JWT-аутентификация
- фоновые задачи через Celery
- периодические задачи через Celery Beat

Стек:
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Nginx
- Docker / Docker Compose
- GitHub Actions (CI/CD)

---

## 🚀 Быстрый запуск (одной командой)

### 1. Создать файл `.env`

```bash
cp .env.sample .env
```

Заполните переменные окружения (пример ниже).

---

### 2. Запуск проекта

```bash
docker compose up --build
```

---

## 🌐 Доступ к сервисам

После запуска:

- API: http://localhost
- Swagger: http://localhost/swagger/
- Redoc: http://localhost/redoc/

---

## 🧩 Сервисы

Проект запускает:

- **backend** — Django + Gunicorn  
- **db** — PostgreSQL  
- **redis** — брокер сообщений  
- **celery** — обработка фоновых задач  
- **celery-beat** — планировщик задач  
- **nginx** — прокси и раздача статики  

---

## ⚙️ Переменные окружения

Пример `.env`:

```env
DEBUG=True
SECRET_KEY=django-insecure-change-me

NAME=drf
USER=postgres
PASSWORD=postgres
HOST=db
PORT=5432

TELEGRAM_BOT_API=

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🔍 Проверка Celery

```bash
docker compose logs celery
docker compose logs celery-beat
```

---

## 🛑 Остановка проекта

```bash
docker compose down
```

Полная очистка:

```bash
docker compose down -v
```

---

## 🐳 Работа в Docker

Важно:

- PostgreSQL доступен по хосту `db`
- Redis доступен по хосту `redis`
- `localhost` внутри контейнеров не используется

---

## 🔁 CI/CD (GitHub Actions)

Pipeline выполняет:

1. Линтинг (flake8)
2. Тесты Django
3. Сборку Docker-образа
4. Публикацию образа в Docker Hub
5. Автоматический деплой на сервер

---

## 🔐 GitHub Secrets

Необходимо добавить в репозиторий:

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_ACCESS_TOKEN`
- `SERVER_IP`
- `SSH_USER`
- `SSH_KEY`
- `DEPLOY_DIR`

---

## 🚀 Деплой на сервер

На сервере должны быть установлены:

- Docker
- Docker Compose
- Git

Первичная настройка:

```bash
git clone <repo_url>
cd <project_folder>
cp .env.sample .env
nano .env
```

---

## ⚙️ Как работает деплой

При пуше в ветку `develop`:

1. GitHub Actions подключается к серверу по SSH  
2. Выполняются команды:

```bash
git pull origin develop
docker compose down
docker compose up -d --build
docker image prune -f
```

3. Проект автоматически обновляется

---

## 🌿 Работа с ветками

- Основная ветка: `develop`
- Ветка задания: `feature/drf_homework`

Создание Pull Request:

```
feature/drf_homework → develop
```

---

## 📁 Структура проекта

```
drf_project/
├── config/
├── users/
├── habits/
├── nginx/
├── Dockerfile
├── docker-compose.yml
├── .env.sample
├── manage.py
└── .github/workflows/ci.yml
```

---

## 🧠 Важно

- Все сервисы запускаются одной командой
- CI/CD полностью автоматизирован
- Деплой выполняется автоматически
- После деплоя приложение работает без ошибок