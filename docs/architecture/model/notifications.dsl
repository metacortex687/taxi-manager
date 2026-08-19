notificationSystem = softwareSystem "Подсистема уведомлений" {
    description "Целевая подключаемая подсистема, получающая изменения PostgreSQL через CDC и формирующая уведомления. Не требуется для работы основного приложения."
    tags "Target Optional"

    debezium = container "CDC-коннектор" {
        description "Читает журнал предзаписи PostgreSQL и публикует события изменения данных."
        technology "Kafka Connect, Debezium 3.6, PostgreSQL logical replication"
        tags "Target Optional"
    }

    kafka = container "Брокер событий" {
        description "Хранит и передаёт события изменения данных потребителям."
        technology "Apache Kafka 4, KRaft"
        tags "Target Optional"
    }

    notificationService = container "Сервис уведомлений" {
        description "Получает события, формирует уведомления и при необходимости обращается к API Taxi-manager."
        technology "Python 3.13, uv, Kafka client"
        tags "Target Optional"
    }

    notificationDatabase = container "Локальная база сервиса" {
        description "Хранит локальные данные и состояние обработки уведомлений."
        technology "SQLite"
        tags "Database,Target Optional"
    }

    kafkaUi = container "Интерфейс Kafka" {
        description "Предоставляет разработчику просмотр брокера, топиков и сообщений."
        technology "Kafka UI"
        tags "Auxiliary,Target Optional"
    }

    flink = container "Потоковая обработка" {
        description "Учебный эксперимент по обработке событий и запросам Flink SQL; не требуется для базового контура уведомлений."
        technology "Apache Flink, Flink SQL"
        tags "Experimental"
    }
}

taxiManager -> notificationSystem.debezium "Предоставляет изменения PostgreSQL через журнал WAL" "PostgreSQL CDC"
notificationSystem.debezium -> notificationSystem.kafka "Публикует события изменения данных" "Kafka protocol, JSON"
notificationSystem.kafka -> notificationSystem.notificationService "Передаёт события потребителю" "Kafka protocol, JSON"
notificationSystem.notificationService -> notificationSystem.notificationDatabase "Сохраняет состояние обработки" "SQLite"
notificationSystem.notificationService -> taxiManager "Обращается к API аутентификации и данным приложения" "REST/JSON over HTTPS"
developer -> notificationSystem.kafkaUi "Просматривает топики и сообщения" "HTTPS"
notificationSystem.kafkaUi -> notificationSystem.kafka "Читает метаданные и сообщения" "Kafka protocol"
notificationSystem.kafka -> notificationSystem.flink "Передаёт поток событий для экспериментальной обработки" "Kafka protocol, JSON" {
    tags "Experimental Flow"
}
