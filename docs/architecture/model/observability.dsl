observability = softwareSystem "Платформа наблюдаемости" {
    description "Принимает от встроенного коллектора Taxi-manager метрики, логи и распределённые трассировки, хранит их и предоставляет средства визуализации и оповещения."
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

taxiManager.djangoWsgi -> taxiManager.alloy "Передаёт метрики и трассировки приложения" "OTLP/gRPC"
taxiManager.djangoAsgi -> taxiManager.alloy "Передаёт метрики и трассировки асинхронных запросов" "OTLP/gRPC"
taxiManager.taskWorker -> taxiManager.alloy "Передаёт метрики и трассировки фоновых заданий" "OTLP/gRPC"
taxiManager.alloy -> taxiManager.nginx "Собирает структурированные access-логи" "Docker logs, logfmt"
taxiManager.alloy -> taxiManager.database "Собирает журналы ошибок PostgreSQL" "Docker logs"
taxiManager.alloy -> taxiManager.rustApi "Собирает журналы высокопроизводительного API" "Docker logs"
taxiManager.alloy -> observability.prometheus "Передаёт метрики" "Prometheus Remote Write"
taxiManager.alloy -> observability.loki "Передаёт логи" "Loki push API"
taxiManager.alloy -> observability.tempo "Передаёт трассировки" "OTLP"

taxiManager.alloy -> observability.cadvisor "Собирает метрики контейнеров" "Prometheus scrape"
observability.nginxExporter -> taxiManager.nginx "Читает показатели Nginx" "HTTP status endpoint"
taxiManager.alloy -> observability.nginxExporter "Собирает метрики Nginx" "Prometheus scrape"
observability.varnishExporter -> taxiManager.varnish "Читает показатели Varnish" "varnishstat"
taxiManager.alloy -> observability.varnishExporter "Собирает метрики Varnish" "Prometheus scrape"
observability.goAccess -> taxiManager.nginx "Анализирует access-логи" "logfmt"

observability.grafana -> observability.prometheus "Запрашивает метрики" "PromQL"
observability.grafana -> observability.loki "Запрашивает логи" "LogQL"
observability.grafana -> observability.tempo "Запрашивает трассировки" "TraceQL/HTTP"
