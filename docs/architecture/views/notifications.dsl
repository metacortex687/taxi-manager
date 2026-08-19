systemContext notificationSystem "NotificationSystemContext" {
    title "C1 — Контекст подсистемы уведомлений"
    description "Подсистема уведомлений является рассматриваемой системой; она получает изменения PostgreSQL через CDC и при необходимости обращается к REST API Taxi-manager."
    include notificationSystem taxiManager
    autoLayout lr 300 220
}

container taxiManager "NotificationContainers" {
    title "Основная логическая архитектура с подсистемой уведомлений"
    description "Дополняет основной контур Taxi-manager цепочкой PostgreSQL WAL → Debezium → исходный топик Kafka → Flink → обработанный топик Kafka → сервис уведомлений."
    include telemetryClient locationIq
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    include notificationSystem.debezium notificationSystem.rawEvents notificationSystem.flink notificationSystem.processedEvents notificationSystem.notificationService notificationSystem.notificationDatabase notificationSystem.kafkaUi
    autoLayout tb 300 200
}

dynamic notificationSystem "NotificationFlow" {
    title "Формирование уведомления из изменения PostgreSQL"
    description "Debezium публикует технические CDC-события. Flink преобразует их и возвращает в отдельный топик Kafka, из которого читает сервис уведомлений."
    1: notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL"
    2: notificationSystem.debezium -> notificationSystem.rawEvents "Публикует техническое CDC-событие"
    3: notificationSystem.rawEvents -> notificationSystem.flink "Передаёт исходное событие"
    4: notificationSystem.flink -> notificationSystem.processedEvents "Публикует преобразованное событие"
    5: notificationSystem.processedEvents -> notificationSystem.notificationService "Передаёт событие предметной области"
    6: notificationSystem.notificationService -> taxiManager.nginx "При необходимости получает данные через REST API"
    7: notificationSystem.notificationService -> notificationSystem.notificationDatabase "Сохраняет состояние обработки"
    autoLayout lr 300 200
}
