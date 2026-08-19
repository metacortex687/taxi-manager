fleetEmployee = person "Сотрудник автопарка" {
    description "Менеджер или диспетчер; эти роли в текущей версии системы не разделяются."
}

administrator = person "Администратор приложения" {
    description "Управляет данными и пользователями через Django Admin."
}

developer = person "Разработчик" {
    description "Изучает OpenAPI-документацию и тестирует REST API."
}

telemetryClient = softwareSystem "Клиент отправки телеметрии" {
    description "Внешнее приложение или устройство отправляет точки трека автомобиля. Конкретный тип датчика пока не определён."
    tags "External System"
}

locationIq = softwareSystem "LocationIQ" {
    description "Внешний сервис геокодирования адресов и зон."
    tags "External System"
}

taxiManager = softwareSystem "Taxi-manager" {
    description "Веб-система для управления автомобилями и водителями, аутентификации пользователей, геокодирования и хранения треков автомобилей."

    !docs taxi-manager/documentation
    !adrs taxi-manager/decisions

    webUi = container "Веб-интерфейс" {
        description "Статические файлы React раздаются Nginx; приложение выполняется в браузере сотрудника автопарка."
        technology "React, JavaScript"
    }

    nginx = container "Входной веб-шлюз" {
        description "Принимает внешние HTTP-запросы, раздаёт статические файлы и маршрутизирует запросы к внутренним приложениям."
        technology "Nginx"
        tags "Gateway"
    }

    djangoWsgi = container "Основное Django-приложение" {
        description "Реализует основной REST API, аутентификацию, Django Admin, бизнес-логику и приём точек трека."
        technology "Python 3.12, Django, Django REST Framework, GeoDjango, WSGI"
    }

    djangoAsgi = container "Асинхронное Django-приложение" {
        description "Обслуживает SSE и асинхронные API-эндпоинты."
        technology "Python 3.12, Django, ASGI"
    }

    taskWorker = container "Фоновый обработчик заданий" {
        description "Обрабатывает очереди reports, geocoding и default; выполняет геокодирование через LocationIQ."
        technology "Python 3.12, Django management command"
        tags "Worker"
    }

    rustApi = container "Rust API" {
        description "Предназначен для переноса из Django операций, которые по результатам измерений становятся узкими местами по производительности. Сейчас читает и создаёт записи vehicle_model одиночными и пакетируемыми обращениями к PostgreSQL."
        technology "Rust, Actix Web, SQLx"
    }

    database = container "База данных Taxi-manager" {
        description "Хранит доменные и географические данные, задания фоновой очереди и результаты геокодирования. LocationIQ не обращается к базе данных напрямую. Схема изменяется миграциями Django."
        technology "PostgreSQL 16, PostGIS 3.5"
        tags "Database"
    }

    swaggerUi = container "Документация API" {
        description "Показывает автоматически сформированную OpenAPI-схему Django и статическую OpenAPI-схему Rust API."
        technology "Swagger UI"
        tags "Auxiliary"
    }
}

fleetEmployee -> taxiManager.webUi "Управляет автомобилями и водителями, просматривает данные о местоположении" "HTTPS через Nginx"
administrator -> taxiManager.nginx "Открывает Django Admin" "HTTPS"
developer -> taxiManager.nginx "Открывает Swagger UI и вызывает REST API" "HTTPS"
telemetryClient -> taxiManager.nginx "Отправляет точки трека автомобиля" "REST/JSON over HTTPS"

taxiManager.nginx -> taxiManager.webUi "Раздаёт статические файлы приложения" "HTTP"
taxiManager.webUi -> taxiManager.nginx "Вызывает REST API" "HTTPS/JSON"
taxiManager.nginx -> taxiManager.djangoWsgi "Маршрутизирует основной REST API, Django Admin и веб-запросы" "uWSGI или HTTP"
taxiManager.nginx -> taxiManager.djangoAsgi "Маршрутизирует SSE и асинхронные запросы" "HTTP"
taxiManager.nginx -> taxiManager.rustApi "Маршрутизирует /api/v1/rust/*" "HTTP"
taxiManager.nginx -> taxiManager.swaggerUi "Маршрутизирует /swagger/*" "HTTP"

taxiManager.djangoWsgi -> taxiManager.database "Читает и изменяет доменные данные; сохраняет фоновые задания в очереди" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.djangoAsgi -> taxiManager.database "Читает и изменяет доменные данные" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> taxiManager.database "Получает задания из очереди и сохраняет результаты" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> locationIq "Запрашивает геокодирование адресов и зон; получает результат в HTTP-ответе" "HTTPS/JSON" {
    tags "External API Call"
}

taxiManager.rustApi -> taxiManager.database "Напрямую читает и изменяет vehicle_model, объединяя часть запросов в пакеты" "SQLx, PostgreSQL protocol" {
    tags "Database Access"
}

