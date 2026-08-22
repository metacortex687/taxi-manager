systemContext notificationSystem "NotificationSystemContext" {
    title "Диаграмма контекста сервиса уведомлений менеджеров"
    description "Сервис уведомлений менеджеров получает изменения основного приложения через CDC, авторизует пользователей через REST API и отправляет сообщения во внешний Чат уведомлений."
    include notificationSystem taxiManager notificationChat fleetEmployee
    autoLayout lr 300 220
}

container notificationSystem "NotificationContainers" {
    title "Диаграмма контейнеров сервиса уведомлений менеджеров"
    description "База данных основного приложения является внешним источником CDC. Debezium публикует исходные события таблиц в Kafka, Flink преобразует их и возвращает в обработанные топики того же кластера. Обработчик уведомлений самостоятельно читает обработанные топики по контракту at-least-once, обновляет локальный контекст организаций и связей с чатами и отправляет сообщения в Чат уведомлений; повторная доставка события допустима."
    include fleetEmployee notificationChat
    include taxiManager.nginx taxiManager.djangoWsgi taxiManager.database
    include notificationSystem.debezium notificationSystem.kafka notificationSystem.flink notificationSystem.notificationService notificationSystem.notificationDatabase notificationSystem.kafkaUi
    autoLayout tb 300 200
}

dynamic notificationSystem "NotificationFlow" {
    title "Формирование уведомления из изменения PostgreSQL"
    description "Показывает путь одного события. Debezium публикует техническое CDC-событие в исходный топик Kafka. Flink преобразует его в интеграционное событие и возвращает в соответствующий обработанный топик того же кластера, который самостоятельно читает Обработчик уведомлений. При повторной доставке этот шаг может быть выполнен более одного раза."
    1: notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL"
    2: notificationSystem.debezium -> notificationSystem.kafka "Публикует событие в исходный топик таблицы"
    3: notificationSystem.kafka -> notificationSystem.flink "Предоставляет исходное CDC-событие"
    4: notificationSystem.flink -> notificationSystem.kafka "Публикует событие в соответствующий обработанный топик"
    5: notificationSystem.notificationService -> notificationSystem.kafka "Читает событие из обработанного топика"
    6: notificationSystem.notificationService -> notificationSystem.notificationDatabase "Находит организацию, назначенных менеджеров и связанные с ними учётные записи чата"
    7: notificationSystem.notificationService -> notificationChat "Отправляет человекочитаемое уведомление в чат"
    autoLayout lr 300 200
}

