fleetEmployee = person "Сотрудник автопарка" {
    description "Менеджер или диспетчер; эти роли в текущей версии системы не разделяются."
}

administrator = person "Администратор приложения" {
    description "Управляет данными и пользователями через Django Admin."
}

externalServiceDeveloper = person "Разработчик внешних сервисов" {
    description "Использует OpenAPI-документацию и REST API приложения для разработки интеграций."
}

telemetryClient = softwareSystem "Клиент телеметрии" {
    description "Внешнее приложение или устройство отправляет точки местоположения автомобилей. Конкретный тип клиента пока не определён."
    tags "External System"
}

locationIq = softwareSystem "LocationIQ" {
    description "Внешний сервис обратного геокодирования."
    tags "External System"
}

taxiManager = softwareSystem "Taxi-manager" {
    description "Веб-система для управления автопарком, хранения поездок и точек телеметрии, геокодирования, формирования отчётов и отслеживания автомобилей."
    tags "Current System"

    webUi = container "Веб-интерфейс" {
        description "Одностраничное React-приложение для сотрудников автопарка; выполняется в браузере, получает данные через REST API и SSE."
        technology "React 19, Vite 8, Mantine, Leaflet"
        tags "Current"
    }

    nginx = container "Входной веб-шлюз" {
        description "Принимает внешние HTTP-соединения, раздаёт статические файлы и маршрутизирует запросы. Буферизует обычный HTTP-трафик и переиспользует настроенные upstream-соединения."
        technology "Nginx"
        tags "Gateway,Current,Diagram Tall"
    }

    djangoWsgi = container "Синхронный REST API" {
        description "Реализует синхронный REST API, аутентификацию, разграничение доступа, Django Admin, бизнес-логику и приём телеметрии."
        technology "Python 3.12, Django 6, Django REST Framework, GeoDjango, WSGI"
        tags "Current"
    }

    djangoAsgi = container "Асинхронный REST API и SSE" {
        description "Асинхронно обрабатывает REST-запросы, обслуживает длительные SSE-соединения и передаёт координаты выбранного автомобиля в браузер в режиме реального времени. Реализовано, но ещё не включено в Jenkins-развёртывание."
        technology "Python 3.12, Django 6, ASGI, Gunicorn, Uvicorn Worker"
        tags "Implemented Not Deployed,Wide API"
    }

    taskWorker = container "Фоновый обработчик заданий" {
        description "Формирует отчёты и выполняет обратное геокодирование по заданиям из фоновых очередей."
        technology "Python 3.12, Django management command, django-tasks-db"
        tags "Worker,Current"
    }

    rustApi = container "Высокопроизводительный асинхронный REST API" {
        description "Выполняет REST-операции, которые по результатам измерений определены как узкие места Синхронного REST API. Текущая реализация читает и создаёт vehicle_model одиночными и пакетными запросами."
        technology "Rust 2021, Actix Web 4, Tokio, SQLx 0.8"
        tags "Prototype,Wide API"
    }

    database = container "База данных" {
        description "Хранит доменные и географические данные, поездки, точки телеметрии, задания фоновой очереди и результаты геокодирования."
        technology "PostgreSQL 16, PostGIS 3.5"
        tags "Database,Current"
    }

    swaggerUi = container "Документация API" {
        description "Показывает автоматически сформированную OpenAPI-схему Django API и статическую схему Rust API из файла rust-open-api-schema.yml, смонтированного только для чтения."
        technology "Swagger UI, OpenAPI"
        tags "Auxiliary,Current,Diagram Tall"
    }

    alloy = container "Коллектор наблюдаемости" {
        description "Собирает метрики, логи и трассировки контейнеров, включая обращения Django к PostgreSQL, и передаёт данные во внешний сервис мониторинга."
        technology "Grafana Alloy, OpenTelemetry, OTLP/gRPC"
        tags "Observability,Current,Diagram Tall"
    }

    cadvisor = container "Метрики контейнеров" {
        description "Предоставляет Grafana Alloy сведения об использовании ресурсов Docker-контейнерами."
        technology "cAdvisor"
        tags "Observability,Auxiliary"
    }

    nginxExporter = container "Экспортёр Nginx" {
        description "Преобразует показатели Nginx в метрики, которые собирает Grafana Alloy."
        technology "Nginx Prometheus Exporter"
        tags "Observability,Auxiliary"
    }

    varnishExporter = container "Экспортёр Varnish" {
        description "Преобразует показатели Varnish в метрики, которые собирает Grafana Alloy."
        technology "Varnish exporter"
        tags "Observability,Auxiliary,Target Optional"
    }

    goAccess = container "Анализ журналов доступа" {
        description "Формирует локальную дополнительную статистику по access-логам Nginx и не передаёт данные в Сервис хранения и визуализации данных мониторинга."
        technology "GoAccess"
        tags "Observability,Auxiliary"
    }

    pgbouncer = container "Пул соединений" {
        description "Переиспользует соединения контейнера «Асинхронный REST API и SSE» с PostgreSQL и предотвращает исчерпание лимита подключений."
        technology "PgBouncer 1.25"
        tags "Current"
    }

    authorizationService = container "Сервис авторизации" {
        description "Проверяет защищённые запросы и формирует доверенный контекст доступа для маршрутизации и формирования ключа HTTP-кэша."
        technology "REST API"
        tags "Target Optional"
    }

    memcached = container "Кэш приложения" {
        description "Предоставляет распределённое кэширование для Django в расширенном окружении."
        technology "Memcached 1.6, PyMemcache 4"
        tags "Target Optional"
    }

    varnish = container "HTTP-кэш" {
        description "Кэширует повторяющиеся HTTP-ответы чтения после маршрутизации Входным веб-шлюзом; для защищённых ответов учитывает доверенный контекст доступа."
        technology "Varnish"
        tags "Target Optional"
    }
}

fleetEmployee -> taxiManager.webUi "Управляет автопарком, просматривает маршруты и получает сформированные отчёты" "HTTP"
administrator -> taxiManager.nginx "Открывает Django Admin" "HTTP"
externalServiceDeveloper -> taxiManager.nginx "Изучает OpenAPI-документацию и вызывает REST API при разработке интеграций" "HTTP"
telemetryClient -> taxiManager.nginx "Отправляет точки местоположения" "REST/JSON over HTTP"

taxiManager.nginx -> taxiManager.webUi "Раздаёт статические файлы и передаёт ответы браузеру" "HTTP"
taxiManager.webUi -> taxiManager.nginx "Вызывает REST API и открывает SSE-соединение" "HTTP/JSON, SSE over HTTP"
taxiManager.nginx -> taxiManager.djangoWsgi "Маршрутизирует синхронные REST-запросы и Django Admin" "uWSGI или HTTP"
taxiManager.nginx -> taxiManager.djangoAsgi "Маршрутизирует асинхронные REST-запросы и запросы онлайн-отслеживания" "HTTP"
taxiManager.djangoAsgi -> taxiManager.nginx "Передаёт поток событий выбранного автомобиля" "SSE over HTTP"
taxiManager.nginx -> taxiManager.rustApi "Маршрутизирует ресурсоёмкие REST-операции" "HTTP/1.1, JSON, keep-alive"
taxiManager.nginx -> taxiManager.swaggerUi "Маршрутизирует веб-интерфейс документации" "HTTP"

taxiManager.djangoWsgi -> taxiManager.database "Читает и изменяет доменные данные; сохраняет фоновые задания" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> taxiManager.database "Получает задания, проверяет сохранённые адреса и сохраняет результаты" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> locationIq "Запрашивает обратное геокодирование" "HTTPS/JSON" {
    tags "External API Call"
}

taxiManager.rustApi -> taxiManager.database "Выполняет одиночные и пакетные операции без Django ORM" "SQLx, PostgreSQL protocol" {
    tags "Database Access"
}

taxiManager.nginx -> taxiManager.authorizationService "Проверяет доступ к защищённым запросам" "REST/JSON over HTTP" {
    tags "Optional Path"
}

taxiManager.nginx -> taxiManager.varnish "Передаёт кэшируемые запросы чтения после маршрутизации и проверки доступа" "HTTP" {
    tags "Optional Path"
}

taxiManager.varnish -> taxiManager.djangoWsgi "Запрашивает отсутствующие в HTTP-кэше ответы" "HTTP" {
    tags "Optional Path"
}

taxiManager.varnish -> taxiManager.rustApi "Запрашивает отсутствующие в HTTP-кэше ресурсоёмкие ответы" "HTTP" {
    tags "Optional Path"
}

taxiManager.djangoWsgi -> taxiManager.pgbouncer "Использует пул соединений в расширенном окружении" "PostgreSQL protocol" {
    tags "Optional Path"
}

taxiManager.djangoAsgi -> taxiManager.pgbouncer "Читает точки выбранного автомобиля через пул соединений" "PostgreSQL protocol" {
    tags "Database Access"
}

taxiManager.taskWorker -> taxiManager.pgbouncer "Использует пул соединений в расширенном окружении" "PostgreSQL protocol" {
    tags "Optional Path"
}

taxiManager.pgbouncer -> taxiManager.database "Переиспользует соединения" "PostgreSQL protocol" {
    tags "Database Access"
}

taxiManager.djangoWsgi -> taxiManager.memcached "Читает и сохраняет кэшированные данные" "Memcached protocol" {
    tags "Optional Path"
}

taxiManager.swaggerUi -> taxiManager.djangoWsgi "Загружает автоматически сформированную схему Django REST API" "OpenAPI/HTTP"
taxiManager.swaggerUi -> taxiManager.rustApi "Читает статическую OpenAPI-схему из смонтированного файла" "Docker bind mount (read-only), OpenAPI/YAML" {
    tags "File Mount"
}
