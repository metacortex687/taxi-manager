container notificationSystem "NotificationContainers" {
    title "Целевой контур уведомлений"
    description "Подключаемая подсистема CDC и событийной доставки. Flink показан как отдельный учебный эксперимент и не требуется для базового потока уведомлений."
    include *
    autoLayout lr 320 220
}

dynamic notificationSystem "NotificationFlow" {
    title "Формирование уведомления из изменения PostgreSQL"
    description "Целевой поток PostgreSQL CDC → Debezium → Kafka → сервис уведомлений."
    1: taxiManager -> notificationSystem.debezium "Предоставляет изменения через журнал WAL"
    2: notificationSystem.debezium -> notificationSystem.kafka "Публикует событие изменения"
    3: notificationSystem.kafka -> notificationSystem.notificationService "Передаёт событие потребителю"
    4: notificationSystem.notificationService -> taxiManager "Проверяет доступ или получает необходимые данные"
    5: notificationSystem.notificationService -> notificationSystem.notificationDatabase "Сохраняет состояние обработки"
    autoLayout lr 300 200
}
