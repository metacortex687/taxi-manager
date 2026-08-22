systemContext notificationSystem "NotificationSystemContext" {
    title "Диаграмма контекста сервиса уведомлений менеджеров"
    description "Сервис уведомлений менеджеров получает изменения основного приложения через CDC, авторизует пользователей через REST API и отправляет сообщения во внешний Чат уведомлений."
    include notificationSystem taxiManager notificationChat fleetEmployee
    exclude "relationship==fleetEmployee->taxiManager"
    autoLayout lr 300 220
}

container notificationSystem "NotificationContainers" {
    title "Диаграмма контейнеров сервиса уведомлений менеджеров"
    description "PostgreSQL является внешним источником CDC. Debezium публикует исходные события в Kafka, Flink преобразует их и возвращает в обработанные топики. Обработчик обновляет локальный контекст и отправляет сообщения. Автоматическое управление offset сейчас не обеспечивает строгую гарантию доставки."
    include fleetEmployee notificationChat
    include taxiManager.nginx taxiManager.djangoWsgi taxiManager.database
    include notificationSystem.debezium notificationSystem.kafka notificationSystem.flink notificationSystem.notificationService notificationSystem.notificationDatabase notificationSystem.kafkaUi
    autoLayout tb 300 200
}

dynamic notificationSystem "NotificationFlow" {
    title "Формирование уведомления из изменения PostgreSQL"
    description "Показывает путь одного изменения PostgreSQL через Debezium, Kafka и Flink к уведомлению в чате. Kafka-клиент обработчика автоматически управляет offset; их фиксация сейчас не привязана к успешной обработке."
    1: notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL"
    2: notificationSystem.debezium -> notificationSystem.kafka "Публикует событие в исходный топик таблицы"
    3: notificationSystem.kafka -> notificationSystem.flink "Предоставляет исходное CDC-событие"
    4: notificationSystem.flink -> notificationSystem.kafka "Публикует событие в соответствующий обработанный топик"
    5: notificationSystem.notificationService -> notificationSystem.kafka "Читает событие из обработанного топика"
    6: notificationSystem.notificationService -> notificationSystem.notificationDatabase "Находит организацию, назначенных менеджеров и связанные с ними учётные записи чата"
    7: notificationSystem.notificationService -> notificationChat "Отправляет человекочитаемое уведомление в чат"
    autoLayout lr 300 200
}
