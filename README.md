## Быстрый запуск демо-версии через Docker Compose

### 1. Создайте отдельную папку для проекта

```bash
mkdir taxi-manager
cd taxi-manager
```

### 2. Скачайте `docker-compose.demo.yaml`

```bash
curl -L -o docker-compose.demo.yaml https://raw.githubusercontent.com/metacortex687/taxi-manager/main/docker-compose.demo.yaml
```

### 3. Создайте и отредактируйте `.env` файл

Скачайте пример env-файла:

```bash
curl -L -o .env.example https://raw.githubusercontent.com/metacortex687/taxi-manager/main/.env.example
```

Создайте рабочий `.env` файл из примера:

```bash
cp .env.example .env
```

Откройте `.env` для редактирования:

```bash
nano .env
```

После редактирования сохраните файл в `nano`:

```text
Ctrl + O
Enter
Ctrl + X
```

### 4. Запустите проект

```bash
docker compose -f docker-compose.demo.yaml up --build
```

### 5. Откройте приложение

После запуска приложение будет доступно по адресу:

```text
http://localhost/
```

Доступные демо-пользователи:

```text
Логин     Пароль
manager1  manager1
manager2  manager2
```

Администратор Django создаётся из значений, указанных в `.env`:

```text
Логин  Пароль
admin  admin
```

---

## Описание `.env` файла

Пример содержимого `.env`:

```env
LOCATIONIQ_KEY=your-locationiq-key

POSTGRES_USER=taxi_manager
POSTGRES_PASSWORD=secret
POSTGRES_DB=taxi_manager

DJANGO_SECRET_KEY=change-me

DJANGO_SUPERUSER_PASSWORD=admin
DJANGO_SUPERUSER_NAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

Описание полей:

| Поле | Описание |
|---|---|
| `LOCATIONIQ_KEY` | API-ключ LocationIQ. Используется для функций, связанных с геоданными и построением маршрутов. Нужно заменить на свой ключ. Без ключа часть гео-функций может не работать. |
| `POSTGRES_USER` | Имя пользователя PostgreSQL, который будет создан внутри Docker-контейнера базы данных. Обычно можно оставить `taxi_manager`. |
| `POSTGRES_PASSWORD` | Пароль пользователя PostgreSQL. Для локального демо-запуска можно оставить `secret`, для публичного сервера лучше заменить. |
| `POSTGRES_DB` | Название базы данных PostgreSQL. Обычно можно оставить `taxi_manager`. |
| `DJANGO_SECRET_KEY` | Секретный ключ Django. Для локального демо-запуска можно оставить `change-me`, для публичного сервера лучше заменить на длинную случайную строку. |
| `DJANGO_SUPERUSER_NAME` | Логин администратора Django. По умолчанию `admin`. |
| `DJANGO_SUPERUSER_PASSWORD` | Пароль администратора Django. По умолчанию `admin`. Для публичного сервера лучше заменить. |
| `DJANGO_SUPERUSER_EMAIL` | Email администратора Django. Можно оставить `admin@example.com` или указать свой email. |


---

## Повторный запуск

### 1. Запуск без пересборки

```bash
docker compose -f docker-compose.demo.yaml up
```

### 2. Запуск с пересборкой образа

```bash
docker compose -f docker-compose.demo.yaml up --build
```

---

## Остановка проекта

### 1. Остановить контейнеры

```bash
docker compose -f docker-compose.demo.yaml down
```

### 2. Остановить контейнеры и удалить базу данных

```bash
docker compose -f docker-compose.demo.yaml down -v
```