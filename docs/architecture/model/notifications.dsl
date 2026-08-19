notificationSystem = softwareSystem "Подсистема уведомлений" {
    description "Подключаемая подсистема, преобразующая технические CDC-события PostgreSQL в события предметной области и формирующая уведомления."
    tags "Target Optional"

    debezium = container "CDC-коннектор" {
        description "Читает журнал предзаписи PostgreSQL и публикует события изменения данных."
        technology "Kafka Connect, Debezium 3.6, PostgreSQL logical replication"
        tags "Target Optional"
    }

    rawEvents = container "Kafka: исходные CDC-события" {
        description "Хранит технические события изменения строк, опубликованные Debezium. Эти события не передаются сервису уведомлений напрямую."
        technology "Apache Kafka 4, KRaft, CDC topic"
        tags "Target Optional"
    }

    flink = container "Потоковая обработка" {
        description "Читает исходные CDC-события из Kafka, фильтрует и преобразует их в события предметной области для уведомлений."
        technology "Apache Flink, Flink SQL"
        tags "Target Optional"
    }

    processedEvents = container "Kafka: обработанные события" {
        description "Хранит подготовленные Flink события, контракт которых соответствует требованиям сервиса уведомлений."
        technology "Apache Kafka 4, KRaft, notification topic"
        tags "Target Optional"
    }

    notificationService = container "Сервис уведомлений" {
        description "Получает из Kafka только обработанные события, формирует уведомления и при необходимости обращается к REST API Taxi-manager."
        technology "Python 3.13, uv, Kafka client"
        tags "Target Optional"
    }

    notificationDatabase = container "Локальная база сервиса" {
        description "Хранит локальные данные и состояние обработки уведомлений."
        technology "SQLite"
        tags "Database,Target Optional"
    }

    kafkaUi = container "Интерфейс Kafka" {
        description "Предоставляет технический интерфейс для просмотра исходного и обработанного топиков Kafka."
        technology "Kafka UI"
        tags "Auxiliary,Target Optional"
    }
}

notificationSystem.debezium -> taxiManager.database "Читает журнал WAL" "PostgreSQL logical replication"
notificationSystem.debezium -> notificationSystem.rawEvents "Публикует технические CDC-события" "Kafka protocol, JSON"
notificationSystem.rawEvents -> notificationSystem.flink "Передаёт исходные события для обработки" "Kafka protocol, JSON"
notificationSystem.flink -> notificationSystem.processedEvents "Публикует преобразованные события" "Kafka protocol, JSON"
notificationSystem.processedEvents -> notificationSystem.notificationService "Передаёт события предметной области" "Kafka protocol, JSON"
notificationSystem.notificationService -> notificationSystem.notificationDatabase "Сохраняет состояние обработки" "SQLite"
notificationSystem.notificationService -> taxiManager.nginx "Получает необходимые данные приложения" "REST/JSON over HTTPS"
notificationSystem.kafkaUi -> notificationSystem.rawEvents "Показывает исходные события" "Kafka protocol"
notificationSystem.kafkaUi -> notificationSystem.processedEvents "Показывает обработанные события" "Kafka protocol"
