notificationChat = softwareSystem "Чат уведомлений" {
    description "Внешний чат на платформе VK, через который сотрудники привязывают учётную запись Taxi-manager и получают уведомления."
    tags "External System"
}

notificationSystem = softwareSystem "Подсистема уведомлений" {
    description "Подключаемая подсистема, преобразующая технические CDC-события PostgreSQL в события предметной области и отправляющая уведомления сотрудникам автопарка."
    tags "Target Optional"

    debezium = container "CDC-коннектор" {
        description "Читает изменения из журнала WAL PostgreSQL посредством логической репликации и публикует исходные CDC-события в Kafka."
        technology "Kafka Connect, Debezium 3.6, PostgreSQL logical replication"
        tags "Target Optional"
    }

    kafka = container "Брокер сообщений" {
        description "Один Kafka-кластер хранит исходный топик с техническими CDC-событиями и обработанный топик с событиями для уведомлений."
        technology "Apache Kafka 4, KRaft"
        tags "Target Optional"
    }

    flink = container "Потоковая обработка" {
        description "Читает исходные CDC-события из Kafka, фильтрует их и преобразует значимые изменения в события для уведомлений."
        technology "Apache Flink, Flink SQL"
        tags "Target Optional"
    }

    notificationService = container "Сервис уведомлений" {
        description "Запускается как Django management command, читает обработанные события, определяет получателей по организациям и отправляет сообщения в Чат уведомлений."
        technology "Python 3.13, Django, uv, Kafka client, VK API"
        tags "Target Optional"
    }

    notificationDatabase = container "Локальное хранилище привязок" {
        description "Хранит привязки пользователей Taxi-manager к чатам и организациям, а также состояние обработки уведомлений; логины и пароли не сохраняются."
        technology "SQLite"
        tags "Database,Target Optional"
    }

    kafkaUi = container "Интерфейс Kafka" {
        description "Предоставляет технический интерфейс для просмотра исходного и обработанного топиков Kafka."
        technology "Kafka UI"
        tags "Auxiliary,Target Optional"
    }
}

fleetEmployee -> notificationChat "Привязывает учётную запись и получает уведомления" "VK"
notificationChat -> notificationSystem.notificationService "Передаёт команды и данные для первичной привязки" "VK API"

notificationSystem.debezium -> taxiManager.database "Читает изменения из журнала WAL" "PostgreSQL logical replication"
notificationSystem.debezium -> notificationSystem.kafka "Публикует исходные технические CDC-события" "Kafka protocol, JSON"
notificationSystem.kafka -> notificationSystem.flink "Передаёт события из исходного топика" "Kafka protocol, JSON"
notificationSystem.flink -> notificationSystem.kafka "Публикует события в обработанный топик" "Kafka protocol, JSON"
notificationSystem.kafka -> notificationSystem.notificationService "Передаёт обработанные события для уведомлений" "Kafka protocol, JSON"
notificationSystem.notificationService -> notificationSystem.notificationDatabase "Хранит привязки и состояние обработки" "SQLite"
notificationSystem.notificationService -> taxiManager.nginx "Авторизует пользователя и получает доступные ему организации" "REST/JSON over HTTPS"
notificationSystem.notificationService -> notificationChat "Отправляет уведомления об изменениях автомобилей" "VK API"
notificationSystem.kafkaUi -> notificationSystem.kafka "Показывает исходный и обработанный топики" "Kafka protocol"
