observability = softwareSystem "Наблюдаемость Taxi-manager" {
    description "Собирает метрики, логи и распределённые трассировки приложения; непрерывное профилирование через Pyroscope может быть подключено дополнительно."
    tags "Observability"

    alloy = container "Коллектор телеметрии" {
        description "Принимает OTLP-телеметрию, собирает метрики и логи контейнеров и направляет данные в Prometheus, Loki и Tempo."
        technology "Grafana Alloy, OpenTelemetry, OTLP/gRPC"
        tags "Observability"
    }

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

    pyroscope = container "Хранилище профилей" {
        description "Опционально принимает и хранит непрерывные профили выполнения приложения."
        technology "Grafana Pyroscope"
        tags "Observability,Database,Target Optional"
    }

    grafana = container "Интерфейс наблюдаемости" {
        description "Предоставляет дашборды, исследование телеметрии и правила оповещений."
        technology "Grafana"
        tags "Observability"
    }

    cadvisor = container "Метрики контейнеров" {
        description "Предоставляет сведения об использовании ресурсов Docker-контейнерами."
        technology "cAdvisor"
        tags "Observability,Auxiliary"
    }

    nginxExporter = container "Экспортёр Nginx" {
        description "Преобразует показатели Nginx в метрики Prometheus."
        technology "Nginx Prometheus Exporter"
        tags "Observability,Auxiliary"
    }

    varnishExporter = container "Экспортёр Varnish" {
        description "Преобразует показатели Varnish в метрики Prometheus."
        technology "Varnish exporter"
        tags "Observability,Auxiliary,Target Optional"
    }

    goAccess = container "Анализ журналов доступа" {
        description "Формирует дополнительную статистику по access-логам Nginx."
        technology "GoAccess"
        tags "Observability,Auxiliary"
    }
}

taxiManager.djangoWsgi -> observability.alloy "Передаёт метрики и трассировки приложения" "OTLP/gRPC"
taxiManager.djangoAsgi -> observability.alloy "Передаёт метрики и трассировки асинхронных запросов" "OTLP/gRPC"
taxiManager.taskWorker -> observability.alloy "Передаёт метрики и трассировки фоновых заданий" "OTLP/gRPC"
observability.alloy -> taxiManager.nginx "Собирает структурированные access-логи" "Docker logs, logfmt"
observability.alloy -> taxiManager.database "Собирает журналы ошибок PostgreSQL" "Docker logs"
observability.alloy -> taxiManager.rustApi "Собирает журналы высокопроизводительного API" "Docker logs"
observability.alloy -> observability.prometheus "Передаёт метрики" "Prometheus Remote Write"
observability.alloy -> observability.loki "Передаёт логи" "Loki push API"
observability.alloy -> observability.tempo "Передаёт трассировки" "OTLP"

observability.alloy -> observability.cadvisor "Собирает метрики контейнеров" "Prometheus scrape"
observability.nginxExporter -> taxiManager.nginx "Читает показатели Nginx" "HTTP status endpoint"
observability.alloy -> observability.nginxExporter "Собирает метрики Nginx" "Prometheus scrape"
observability.varnishExporter -> taxiManager.varnish "Читает показатели Varnish" "varnishstat"
observability.alloy -> observability.varnishExporter "Собирает метрики Varnish" "Prometheus scrape"
observability.goAccess -> taxiManager.nginx "Анализирует access-логи" "logfmt"

taxiManager.djangoWsgi -> observability.pyroscope "Опционально передаёт профили выполнения" "Pyroscope protocol" {
    tags "Optional Path"
}
taxiManager.taskWorker -> observability.pyroscope "Опционально передаёт профили фонового обработчика" "Pyroscope protocol" {
    tags "Optional Path"
}

observability.grafana -> observability.prometheus "Запрашивает метрики" "PromQL"
observability.grafana -> observability.loki "Запрашивает логи" "LogQL"
observability.grafana -> observability.tempo "Запрашивает трассировки" "TraceQL/HTTP"
observability.grafana -> observability.pyroscope "При подключении запрашивает профили" "HTTP API" {
    tags "Optional Path"
}
