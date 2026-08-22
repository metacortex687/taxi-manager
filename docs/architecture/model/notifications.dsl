notificationChat = softwareSystem "Чат уведомлений" {
    description "Внешний чат на платформе VK для авторизации сотрудников в приложении Taxi-manager и получения уведомлений."
    tags "External System"
}

notificationSystem = softwareSystem "Сервис уведомлений менеджеров" {
    description "Преобразует CDC-события PostgreSQL в интеграционные события и отправляет менеджерам уведомления об изменениях автомобилей."
    tags "Implemented Not Deployed,Diagram Tall"

    debezium = container "CDC-коннектор" {
        description "Читает изменения из журнала WAL PostgreSQL посредством логической репликации и публикует исходные CDC-события в Kafka."
        technology "Kafka Connect, Debezium 3.6, PostgreSQL logical replication"
        tags "Implemented Not Deployed"
    }

    kafka = container "Брокер сообщений" {
        description "Хранит исходные CDC-события, обработанные события домена и позиции чтения consumer groups."
        technology "Apache Kafka 4, KRaft"
        tags "Implemented Not Deployed,Diagram Extra Tall"
    }

    flink = container "Обработка событий" {
        description "Читает исходные CDC-топики Kafka, фильтрует события и преобразует значимые изменения в обработанные топики для уведомлений и локального контекста."
        technology "Apache Flink, Flink SQL"
        tags "Implemented Not Deployed"
    }

    notificationService = container "Обработчик уведомлений" {
        description "Читает обработанные события, обновляет локальный контекст и отправляет уведомления в Чат уведомлений. Kafka-клиент управляет offset автоматически и фиксирует их независимо от результата обработки."
        technology "Python 3.13, Django, Kafka client, VK API"
        tags "Implemented Not Deployed,Diagram Extra Tall"
    }

    notificationDatabase = container "Хранилище контекста" {
        description "Хранит организации, модели автомобилей, назначения менеджеров и связи учётных записей приложения с учётными записями чата. Используется для выбора получателей и формирования сообщений; учётные данные не сохраняются."
        technology "SQLite"
        tags "Database,Implemented Not Deployed,Diagram Extra Tall"
    }

    kafkaUi = container "Интерфейс Kafka" {
        description "Предоставляет технический интерфейс для просмотра исходных и обработанных топиков Kafka."
        technology "Kafka UI"
        tags "Auxiliary,Implemented Not Deployed"
    }
}

fleetEmployee -> notificationChat "Авторизуется в Taxi-manager и получает уведомления" "VK"
notificationChat -> notificationSystem.notificationService "Передаёт команды и данные для авторизации" "VK API"

notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL" "PostgreSQL logical replication"
notificationSystem.debezium -> notificationSystem.kafka "Публикует исходные технические CDC-события по таблицам" "Kafka protocol, JSON"
notificationSystem.kafka -> notificationSystem.flink "Предоставляет события из исходных топиков" "Kafka protocol, JSON"
notificationSystem.flink -> notificationSystem.kafka "Публикует события в обработанные топики" "Kafka protocol, JSON"
notificationSystem.notificationService -> notificationSystem.kafka "Читает обработанные события для локального контекста и уведомлений" "Kafka protocol, JSON"
notificationSystem.notificationService -> notificationSystem.notificationDatabase "Обновляет и читает локальный контекст организаций, моделей и связей с чатами" "SQLite"
notificationSystem.notificationService -> taxiManager.nginx "Авторизует пользователя и получает доступные ему организации" "REST/JSON over HTTP"
notificationSystem.notificationService -> notificationChat "Отправляет уведомления об изменениях автомобилей" "VK API"
notificationSystem.kafkaUi -> notificationSystem.kafka "Показывает исходные и обработанные топики" "Kafka protocol"
