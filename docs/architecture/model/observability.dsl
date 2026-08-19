observability = softwareSystem "Наблюдаемость Taxi-manager" {
    description "Собирает и предоставляет метрики, логи, распределённые трассировки и профили выполнения приложения."
    tags "Observability"

    alloy = container "Коллектор телеметрии" {
        description "Принимает OTLP-телеметрию и собирает логи контейнеров, после чего направляет данные в специализированные хранилища."
        technology "Grafana Alloy, OpenTelemetry, OTLP/gRPC"
        tags "Observability"
    }

    prometheus = container "Хранилище метрик" {
        description "Собирает метрики приложения, контейнеров и экспортёров и выполняет PromQL-запросы."
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
        description "Принимает и хранит непрерывные профили выполнения приложения."
        technology "Grafana Pyroscope"
        tags "Observability,Database"
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

taxiManager.djangoWsgi -> observability.alloy "Передаёт трассировки приложения" "OTLP/gRPC"
taxiManager.djangoAsgi -> observability.alloy "Передаёт трассировки асинхронных запросов" "OTLP/gRPC"
taxiManager.taskWorker -> observability.alloy "Передаёт трассировки фоновых заданий" "OTLP/gRPC"
observability.alloy -> taxiManager.nginx "Собирает структурированные access-логи" "Docker logs, logfmt"
observability.alloy -> taxiManager.database "Собирает журналы ошибок PostgreSQL" "Docker logs"
observability.alloy -> observability.loki "Передаёт логи" "Loki push API"
observability.alloy -> observability.tempo "Передаёт трассировки" "OTLP"

observability.prometheus -> taxiManager.djangoWsgi "Собирает метрики Django" "Prometheus scrape"
observability.prometheus -> observability.alloy "Собирает служебные метрики коллектора" "Prometheus scrape"
observability.prometheus -> observability.cadvisor "Собирает метрики контейнеров" "Prometheus scrape"
observability.nginxExporter -> taxiManager.nginx "Читает показатели Nginx" "HTTP status endpoint"
observability.prometheus -> observability.nginxExporter "Собирает метрики Nginx" "Prometheus scrape"
observability.varnishExporter -> taxiManager.varnish "Читает показатели Varnish" "varnishstat"
observability.prometheus -> observability.varnishExporter "Собирает метрики Varnish" "Prometheus scrape"
observability.goAccess -> taxiManager.nginx "Анализирует access-логи" "logfmt"

taxiManager.djangoWsgi -> observability.pyroscope "Передаёт профили выполнения" "Pyroscope protocol"
taxiManager.taskWorker -> observability.pyroscope "Передаёт профили фонового обработчика" "Pyroscope protocol"

observability.grafana -> observability.prometheus "Запрашивает метрики" "PromQL"
observability.grafana -> observability.loki "Запрашивает логи" "LogQL"
observability.grafana -> observability.tempo "Запрашивает трассировки" "TraceQL/HTTP"
observability.grafana -> observability.pyroscope "Запрашивает профили" "HTTP API"
developer -> observability.grafana "Анализирует состояние приложения и результаты тестов" "HTTPS"
