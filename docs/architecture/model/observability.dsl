supportSpecialist = person "Специалист сопровождения" {
    description "Контролирует техническое состояние приложения и получает эксплуатационные оповещения."
}

mailService = softwareSystem "Почтовый сервис" {
    description "Внешний SMTP-сервис доставляет email-оповещения Сервиса хранения и визуализации данных мониторинга Специалисту сопровождения."
    tags "External System"
}

observability = softwareSystem "Сервис хранения и визуализации данных мониторинга" {
    description "Принимает телеметрию от коллектора, хранит и визуализирует её, оповещает специалиста сопровождения."
    tags "Observability"

    prometheus = container "Хранилище метрик" {
        description "Принимает метрики, направленные Alloy, хранит их и выполняет PromQL-запросы."
        technology "Prometheus"
        tags "Observability,Database"
    }

    loki = container "Хранилище логов" {
        description "Хранит логи приложения, Nginx и PostgreSQL и выполняет LogQL-запросы."
        technology "Grafana Loki"
        tags "Observability,Database"
    }

    tempo = container "Хранилище трассировок" {
        description "Хранит распределённые трассировки; используется также Jenkins-проверкой возможных N+1-запросов."
        technology "Grafana Tempo"
        tags "Observability,Database"
    }

    grafana = container "Интерфейс наблюдаемости" {
        description "Предоставляет дашборды, исследование телеметрии и правила оповещений; при срабатывании правила отправляет email через Почтовый сервис."
        technology "Grafana"
        tags "Observability"
    }

}

taxiManager -> observability "Передаёт метрики, распределённые трассировки и логи" "OTLP, Prometheus Remote Write, Loki push API"
alloyToObservability = taxiManager.alloy -> observability "Передаёт метрики, распределённые трассировки и логи" "OTLP, Prometheus Remote Write, Loki push API"

taxiManager.djangoWsgi -> taxiManager.alloy "Передаёт трассировки HTTP-запросов, включая SQL-операции Django → PostgreSQL" "OpenTelemetry, OTLP/gRPC"
taxiManager.djangoAsgi -> taxiManager.alloy "Передаёт трассировки асинхронных запросов, включая обращения к PostgreSQL" "OpenTelemetry, OTLP/gRPC"
taxiManager.taskWorker -> taxiManager.alloy "Передаёт трассировки фоновых заданий" "OpenTelemetry, OTLP/gRPC"
taxiManager.alloy -> taxiManager.djangoWsgi "Собирает метрики приложения" "Prometheus scrape"
taxiManager.alloy -> taxiManager.nginx "Собирает структурированные access-логи" "Docker logs, logfmt"
taxiManager.alloy -> taxiManager.database "Собирает журналы ошибок PostgreSQL" "Docker logs"
taxiManager.alloy -> taxiManager.rustApi "Собирает журналы Высокопроизводительного асинхронного REST API" "Docker logs"
taxiManager.alloy -> observability.prometheus "Передаёт метрики" "Prometheus Remote Write"
taxiManager.alloy -> observability.loki "Передаёт логи" "Loki push API"
taxiManager.alloy -> observability.tempo "Передаёт трассировки" "OTLP"

taxiManager.alloy -> taxiManager.cadvisor "Собирает метрики контейнеров" "Prometheus scrape"
taxiManager.nginxExporter -> taxiManager.nginx "Читает показатели Nginx" "HTTP status endpoint"
taxiManager.alloy -> taxiManager.nginxExporter "Собирает метрики Nginx" "Prometheus scrape"
taxiManager.varnishExporter -> taxiManager.varnish "Читает показатели Varnish" "varnishstat"
taxiManager.alloy -> taxiManager.varnishExporter "Собирает метрики Varnish" "Prometheus scrape"
taxiManager.goAccess -> taxiManager.nginx "Анализирует access-логи" "logfmt"

observability.grafana -> observability.prometheus "Запрашивает метрики" "PromQL"
observability.grafana -> observability.loki "Запрашивает логи" "LogQL"
observability.grafana -> observability.tempo "Запрашивает трассировки" "TraceQL/HTTP"
observability.grafana -> mailService "Отправляет эксплуатационные оповещения" "SMTP"
mailService -> supportSpecialist "Доставляет оповещения" "Email"

