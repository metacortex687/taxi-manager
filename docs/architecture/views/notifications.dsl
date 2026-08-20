systemContext notificationSystem "NotificationSystemContext" {
    title "C1 — Контекст подсистемы уведомлений"
    description "Подсистема уведомлений получает изменения Taxi-manager через CDC, авторизует пользователей через REST API и отправляет сообщения во внешний Чат уведомлений."
    include notificationSystem taxiManager notificationChat fleetEmployee
    autoLayout lr 300 220
}

container notificationSystem "NotificationContainers" {
    title "Основная логическая архитектура с подсистемой уведомлений"
    description "База данных Taxi-manager является внешним источником CDC. Debezium публикует исходные события в Kafka, Flink преобразует их и возвращает в обработанный топик того же кластера, после чего Сервис уведомлений отправляет сообщения в Чат уведомлений."
    include fleetEmployee notificationChat
    include taxiManager.nginx taxiManager.djangoWsgi taxiManager.database
    include notificationSystem.debezium notificationSystem.kafka notificationSystem.flink notificationSystem.notificationService notificationSystem.notificationDatabase notificationSystem.kafkaUi
    autoLayout tb 300 200
}

dynamic notificationSystem "NotificationFlow" {
    title "Формирование уведомления из изменения PostgreSQL"
    description "Debezium публикует техническое CDC-событие в исходный топик Kafka. Flink преобразует его и возвращает в обработанный топик того же кластера, из которого читает Сервис уведомлений."
    1: notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL"
    2: notificationSystem.debezium -> notificationSystem.kafka "Публикует событие в исходный топик"
    3: notificationSystem.kafka -> notificationSystem.flink "Передаёт исходное CDC-событие"
    4: notificationSystem.flink -> notificationSystem.kafka "Публикует событие в обработанный топик"
    5: notificationSystem.kafka -> notificationSystem.notificationService "Передаёт обработанное событие"
    6: notificationSystem.notificationService -> notificationSystem.notificationDatabase "Определяет получателей по привязкам к организациям"
    7: notificationSystem.notificationService -> notificationChat "Отправляет уведомления в чат"
    autoLayout lr 300 200
}
