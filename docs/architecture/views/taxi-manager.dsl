systemContext taxiManager "TaxiManagerSystemContext" {
    title "C1 — Диаграмма контекста системы Taxi-manager"
    description "Показывает пользователей, границу Taxi-manager, непосредственно используемые внешние системы и Платформу наблюдаемости. Специалист сопровождения, CI/CD и Система уведомлений менеджеров вынесены в отдельные представления."
    include taxiManager fleetEmployee administrator externalServiceDeveloper telemetryClient locationIq observability
    exclude notificationSystem
    autoLayout lr 300 220
    default
}

container taxiManager "TaxiManagerLogicalContainers" {
    title "C2 — Диаграмма контейнеров Taxi-manager"
    description "Показывает основной функциональный контур, контейнер «Коллектор наблюдаемости» на Grafana Alloy, подключение Асинхронного Django-приложения к PostgreSQL через PgBouncer и прототип Высокопроизводительного API. Отдельная файловая связь показывает монтирование статической OpenAPI-схемы Высокопроизводительного API в Документацию API только для чтения. Система уведомлений менеджеров вынесена в собственный набор представлений."
    include fleetEmployee administrator externalServiceDeveloper telemetryClient locationIq observability
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.pgbouncer taxiManager.database taxiManager.swaggerUi taxiManager.alloy
    exclude notificationSystem
    exclude "relationship.tag==Optional Path"
    autoLayout tb 320 220
}

container taxiManager "TaxiManagerExtendedRuntime" {
    title "C2 — Расширенная диаграмма контейнеров Taxi-manager"
    description "Показывает логические контейнеры приложения и дополнительные компоненты выполнения без стека наблюдаемости и CI/CD."
    include telemetryClient locationIq
    include taxiManager.webUi taxiManager.varnish taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.swaggerUi taxiManager.pgbouncer taxiManager.memcached taxiManager.database
    exclude notificationSystem
    autoLayout tb 320 220
}

dynamic taxiManager "TaxiManagerLiveTrackingFlow" {
    title "Онлайн-отслеживание автомобиля через SSE"
    description "Сотрудник автопарка отслеживает выбранный автомобиль через веб-интерфейс. Клиент телеметрии отправляет новые точки через Синхронное Django-приложение, а Асинхронное Django-приложение читает их из PostgreSQL через PgBouncer и передаёт браузеру по SSE."
    1: fleetEmployee -> taxiManager.webUi "Открывает отслеживание выбранного автомобиля"
    2: taxiManager.webUi -> taxiManager.nginx "Открывает SSE-соединение"
    3: taxiManager.nginx -> taxiManager.djangoAsgi "Передаёт запрос онлайн-отслеживания"
    4: telemetryClient -> taxiManager.nginx "Отправляет новую точку автомобиля"
    5: taxiManager.nginx -> taxiManager.djangoWsgi "Передаёт точку через REST API"
    6: taxiManager.djangoWsgi -> taxiManager.database "Сохраняет точку"
    7: taxiManager.djangoAsgi -> taxiManager.pgbouncer "Запрашивает новые точки выбранного автомобиля"
    8: taxiManager.pgbouncer -> taxiManager.database "Передаёт запрос через пул соединений"
    9: taxiManager.djangoAsgi -> taxiManager.nginx "Передаёт новые точки по SSE"
    10: taxiManager.nginx -> taxiManager.webUi "Доставляет SSE-события браузеру"
    autoLayout tb 280 200
}

dynamic taxiManager "TaxiManagerGeocodingFlow" {
    title "Геокодирование адреса через фоновое задание"
    description "Синхронное Django-приложение сначала ищет сохранённый адрес. При его отсутствии создаётся фоновое задание; обработчик повторно проверяет базу, обращается к LocationIQ только при отсутствии результата и сохраняет адрес для повторного использования."
    1: taxiManager.djangoWsgi -> taxiManager.database "Ищет сохранённые адреса начальной и конечной точек"
    2: taxiManager.djangoWsgi -> taxiManager.database "При отсутствии адреса сохраняет задание геокодирования"
    3: taxiManager.taskWorker -> taxiManager.database "Получает задание и повторно проверяет наличие адреса"
    4: taxiManager.taskWorker -> locationIq "При отсутствии адреса запрашивает обратное геокодирование"
    5: taxiManager.taskWorker -> taxiManager.database "Сохраняет адрес и его географическую область для повторного использования"
    autoLayout lr 280 200
}
