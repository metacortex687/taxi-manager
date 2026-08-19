systemContext taxiManager "TaxiManagerSystemContext" {
    title "C1 — Контекст системы Taxi-manager"
    description "Показывает пользователей, границу работающего приложения Taxi-manager и непосредственно используемые им внешние программные системы."
    include taxiManager fleetEmployee administrator externalServiceDeveloper telemetryClient locationIq
    exclude notificationSystem
    autoLayout lr 300 220
    default
}

container taxiManager "TaxiManagerLogicalContainers" {
    title "C2 — Основная логическая архитектура Taxi-manager"
    description "Показывает основной функциональный контур, ASGI-приложение и прототип Rust API. Целевая подсистема уведомлений вынесена в собственный набор представлений. Статус элементов задаётся стилем и описанием."
    include fleetEmployee administrator externalServiceDeveloper telemetryClient locationIq
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    exclude notificationSystem
    autoLayout tb 320 220
}

container taxiManager "TaxiManagerExtendedRuntime" {
    title "Расширенный контур выполнения Taxi-manager"
    description "Показывает логические контейнеры приложения и дополнительные компоненты выполнения без стека наблюдаемости и CI/CD."
    include telemetryClient locationIq
    include taxiManager.webUi taxiManager.varnish taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.swaggerUi taxiManager.pgbouncer taxiManager.memcached taxiManager.database
    exclude notificationSystem
    autoLayout tb 320 220
}

component taxiManager.djangoWsgi "TaxiManagerWsgiComponents" {
    title "C3 — Компоненты основного Django-приложения"
    description "Предварительное компонентное представление. Его следует сверить с фактической структурой пакетов и уточнить после просмотра исходного кода."
    include taxiManager.djangoWsgi.restApi taxiManager.djangoWsgi.accessControl taxiManager.djangoWsgi.djangoAdmin taxiManager.djangoWsgi.applicationServices taxiManager.djangoWsgi.domainModel taxiManager.djangoWsgi.repositories taxiManager.djangoWsgi.taskPublisher taxiManager.djangoWsgi.openApiSchema
    include administrator telemetryClient taxiManager.nginx taxiManager.swaggerUi taxiManager.database
    autoLayout lr 320 220
}

dynamic taxiManager "TaxiManagerLiveTrackingFlow" {
    title "Онлайн-отслеживание автомобиля через SSE"
    description "Клиент запрашивает данные выбранного автомобиля, после чего ASGI-приложение начинает передавать точки через SSE. Способ обнаружения очередной записи оставлен на уровне чтения данных и должен быть уточнён по реализации endpoint."
    1: taxiManager.webUi -> taxiManager.nginx "Открывает поток отслеживания выбранного автомобиля"
    2: taxiManager.nginx -> taxiManager.djangoAsgi "Маршрутизирует запрос онлайн-отслеживания"
    3: taxiManager.djangoAsgi -> taxiManager.database "Получает доступные точки выбранного автомобиля"
    4: taxiManager.djangoAsgi -> taxiManager.nginx "Начинает передавать события"
    5: taxiManager.nginx -> taxiManager.webUi "Передаёт события браузеру"
    6: telemetryClient -> taxiManager.nginx "Отправляет очередную точку местоположения"
    7: taxiManager.nginx -> taxiManager.djangoWsgi "Маршрутизирует запрос телеметрии"
    8: taxiManager.djangoWsgi -> taxiManager.database "Сохраняет точку"
    9: taxiManager.djangoAsgi -> taxiManager.database "Получает очередные точки выбранного автомобиля"
    10: taxiManager.djangoAsgi -> taxiManager.nginx "Передаёт новые события"
    11: taxiManager.nginx -> taxiManager.webUi "Обновляет поток в браузере"
    autoLayout lr 260 180
}

dynamic taxiManager "TaxiManagerGeocodingFlow" {
    title "Геокодирование адреса через фоновое задание"
    description "LocationIQ взаимодействует только с фоновым обработчиком и не имеет прямого доступа к PostgreSQL."
    1: taxiManager.djangoWsgi -> taxiManager.database "Сохраняет задание геокодирования"
    2: taxiManager.taskWorker -> taxiManager.database "Получает задание из очереди"
    3: taxiManager.taskWorker -> locationIq "Запрашивает и получает результат геокодирования"
    4: taxiManager.taskWorker -> taxiManager.database "Сохраняет результат геокодирования"
    autoLayout lr 280 200
}
