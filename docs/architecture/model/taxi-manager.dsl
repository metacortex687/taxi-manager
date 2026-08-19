fleetEmployee = person "Сотрудник автопарка" {
    description "Менеджер или диспетчер; эти роли в текущей версии системы не разделяются."
}

administrator = person "Администратор приложения" {
    description "Управляет данными и пользователями через Django Admin."
}

developer = person "Разработчик" {
    description "Изучает документацию, тестирует REST API и сопровождает приложение."
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
    description "Веб-система для управления автопарком, хранения поездок и точек телеметрии, геокодирования и отслеживания автомобилей."
    tags "Current System"

    webUi = container "Веб-интерфейс" {
        description "Одностраничное React-приложение для сотрудников автопарка; выполняется в браузере, получает данные через REST API и SSE."
        technology "React 19, Vite 8, Mantine, Leaflet"
        tags "Current"
    }

    nginx = container "Входной веб-шлюз" {
        description "Принимает внешние HTTP-запросы, раздаёт статические файлы и маршрутизирует запросы к внутренним приложениям."
        technology "Nginx"
        tags "Gateway,Current"
    }

    djangoWsgi = container "Основное Django-приложение" {
        description "Реализует синхронный REST API, аутентификацию, разграничение доступа, Django Admin, бизнес-логику и приём телеметрии."
        technology "Python 3.12, Django 6, Django REST Framework, GeoDjango, WSGI"
        tags "Current"

        restApi = component "REST API" {
            description "Предоставляет операции управления организациями, автомобилями, поездками и точками телеметрии."
            technology "Django REST Framework, django-filter, djangorestframework-gis"
        }

        accessControl = component "Аутентификация и контроль доступа" {
            description "Аутентифицирует пользователей и ограничивает доступ набором назначенных организаций."
            technology "Django authentication, Djoser, DRF permissions"
        }

        djangoAdmin = component "Административный интерфейс" {
            description "Предоставляет администратору полный доступ к данным и пользователям."
            technology "Django Admin"
        }

        applicationServices = component "Прикладные сценарии" {
            description "Координирует операции управления автопарком, поездками, геотрекингом, геокодированием и отчётами."
            technology "Python, Django application layer"
        }

        domainModel = component "Доменная модель" {
            description "Содержит модели и правила предметной области Taxi-manager."
            technology "Python, Django models"
        }

        repositories = component "Репозитории и Unit of Work" {
            description "Инкапсулирует доступ к данным и границы транзакций."
            technology "Django ORM, PostgreSQL, Unit of Work"
        }

        taskPublisher = component "Постановка фоновых заданий" {
            description "Создаёт задания в очередях reports, geocoding и default."
            technology "django-tasks-db"
        }

        openApiSchema = component "Формирование OpenAPI-схемы" {
            description "Формирует машиночитаемое описание REST API Django."
            technology "drf-spectacular, OpenAPI"
        }
    }

    djangoAsgi = container "Асинхронное Django-приложение" {
        description "Обслуживает SSE-соединения и передаёт клиенту точки выбранного автомобиля по мере их получения. Реализовано, но ещё не включено в Jenkins-развёртывание."
        technology "Python 3.12, Django 6, ASGI, Gunicorn, Uvicorn Worker"
        tags "Implemented Not Deployed"
    }

    taskWorker = container "Фоновый обработчик заданий" {
        description "Обрабатывает очереди reports, geocoding и default; выполняет геокодирование через LocationIQ и сохраняет результаты."
        technology "Python 3.12, Django management command, django-tasks-db"
        tags "Worker,Current"
    }

    rustApi = container "Высокопроизводительный API" {
        description "Прототип для операций, которые по результатам измерений будут определены как узкие места Django API. Текущая реализация читает и создаёт vehicle_model одиночными и пакетными запросами."
        technology "Rust 2021, Actix Web 4, Tokio, SQLx 0.8"
        tags "Prototype"
    }

    database = container "База данных Taxi-manager" {
        description "Хранит доменные и географические данные, поездки, точки телеметрии, задания фоновой очереди и результаты геокодирования."
        technology "PostgreSQL 16, PostGIS 3.5"
        tags "Database,Current"
    }

    swaggerUi = container "Документация API" {
        description "Показывает автоматически сформированную OpenAPI-схему Django и статическую OpenAPI-схему Rust API."
        technology "Swagger UI, OpenAPI"
        tags "Auxiliary,Current"
    }

    pgbouncer = container "Пул соединений" {
        description "Переиспользует соединения приложения с PostgreSQL в расширенном окружении."
        technology "PgBouncer 1.25"
        tags "Target Optional"
    }

    memcached = container "Кеш приложения" {
        description "Предоставляет распределённое кеширование для Django в расширенном окружении."
        technology "Memcached 1.6, PyMemcache 4"
        tags "Target Optional"
    }

    varnish = container "HTTP-кеш" {
        description "Кеширует HTTP-ответы перед Nginx в расширенном окружении."
        technology "Varnish"
        tags "Target Optional"
    }
}

fleetEmployee -> taxiManager.webUi "Управляет автопарком и просматривает маршруты" "HTTPS"
administrator -> taxiManager.nginx "Открывает Django Admin" "HTTPS"
developer -> taxiManager.nginx "Открывает Swagger UI и вызывает REST API" "HTTPS"
telemetryClient -> taxiManager.nginx "Отправляет точки местоположения" "REST/JSON over HTTPS"

taxiManager.nginx -> taxiManager.webUi "Раздаёт статические файлы и передаёт ответы браузеру" "HTTP/HTTPS"
taxiManager.webUi -> taxiManager.nginx "Вызывает REST API и открывает SSE-соединение" "HTTPS/JSON, SSE"
taxiManager.nginx -> taxiManager.djangoWsgi "Маршрутизирует REST API и Django Admin" "uWSGI или HTTP"
taxiManager.nginx -> taxiManager.djangoAsgi "Маршрутизирует запросы онлайн-отслеживания" "HTTP/SSE"
taxiManager.djangoAsgi -> taxiManager.nginx "Передаёт поток событий выбранного автомобиля" "SSE over HTTP"
taxiManager.nginx -> taxiManager.rustApi "Маршрутизирует высоконагруженные операции прототипа" "HTTP/JSON"
taxiManager.nginx -> taxiManager.swaggerUi "Маршрутизирует веб-интерфейс документации" "HTTP"

taxiManager.djangoWsgi -> taxiManager.database "Читает и изменяет доменные данные; сохраняет фоновые задания" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.djangoAsgi -> taxiManager.database "Получает точки выбранного автомобиля для передачи через SSE" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> taxiManager.database "Получает задания и сохраняет результаты" "Django ORM, SQL" {
    tags "Database Access"
}

taxiManager.taskWorker -> locationIq "Запрашивает обратное геокодирование" "HTTPS/JSON" {
    tags "External API Call"
}

taxiManager.rustApi -> taxiManager.database "Выполняет одиночные и пакетные операции без Django ORM" "SQLx, PostgreSQL protocol" {
    tags "Database Access"
}

taxiManager.varnish -> taxiManager.nginx "Передаёт запросы, отсутствующие в HTTP-кеше" "HTTP" {
    tags "Optional Path"
}

taxiManager.djangoWsgi -> taxiManager.pgbouncer "Использует пул соединений в расширенном окружении" "PostgreSQL protocol" {
    tags "Optional Path"
}

taxiManager.djangoAsgi -> taxiManager.pgbouncer "Использует пул соединений в расширенном окружении" "PostgreSQL protocol" {
    tags "Optional Path"
}

taxiManager.taskWorker -> taxiManager.pgbouncer "Использует пул соединений в расширенном окружении" "PostgreSQL protocol" {
    tags "Optional Path"
}

taxiManager.pgbouncer -> taxiManager.database "Переиспользует соединения" "PostgreSQL protocol" {
    tags "Database Access,Optional Path"
}

taxiManager.djangoWsgi -> taxiManager.memcached "Читает и сохраняет кешированные данные" "Memcached protocol" {
    tags "Optional Path"
}

taxiManager.nginx -> taxiManager.djangoWsgi.restApi "Направляет запросы REST API" "HTTP/uWSGI"
taxiManager.nginx -> taxiManager.djangoWsgi.djangoAdmin "Направляет административные запросы" "HTTP/uWSGI"
telemetryClient -> taxiManager.djangoWsgi.restApi "Передаёт точки телеметрии через внешний шлюз" "REST/JSON"
administrator -> taxiManager.djangoWsgi.djangoAdmin "Управляет пользователями и данными" "HTTPS через Nginx"

taxiManager.djangoWsgi.restApi -> taxiManager.djangoWsgi.accessControl "Проверяет аутентификацию и доступ к организациям"
taxiManager.djangoWsgi.restApi -> taxiManager.djangoWsgi.applicationServices "Запускает прикладные сценарии"
taxiManager.djangoWsgi.djangoAdmin -> taxiManager.djangoWsgi.applicationServices "Выполняет административные операции"
taxiManager.djangoWsgi.applicationServices -> taxiManager.djangoWsgi.domainModel "Применяет правила предметной области"
taxiManager.djangoWsgi.applicationServices -> taxiManager.djangoWsgi.repositories "Читает и сохраняет данные"
taxiManager.djangoWsgi.applicationServices -> taxiManager.djangoWsgi.taskPublisher "Создаёт фоновые задания"
taxiManager.djangoWsgi.repositories -> taxiManager.database "Выполняет транзакции и запросы" "Django ORM, SQL" {
    tags "Database Access"
}
taxiManager.djangoWsgi.taskPublisher -> taxiManager.database "Сохраняет задания очереди" "Django ORM, SQL" {
    tags "Database Access"
}
taxiManager.djangoWsgi.openApiSchema -> taxiManager.djangoWsgi.restApi "Описывает операции и структуры данных"
taxiManager.swaggerUi -> taxiManager.djangoWsgi.openApiSchema "Загружает схему Django API" "OpenAPI/HTTP"
