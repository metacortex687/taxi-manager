systemLandscape "RuntimeWithObservability" {
    title "Taxi-manager и Платформа наблюдаемости"
    description "Показывает Taxi-manager со встроенным коллектором телеметрии и внешнюю Платформу наблюдаемости без CI/CD и подсистемы уведомлений."
    include telemetryClient locationIq taxiManager observability
    autoLayout lr 320 230
}

container taxiManager "ObservabilityContainers" {
    title "Основная логическая архитектура со стеком телеметрии"
    description "Встроенный в Taxi-manager Grafana Alloy собирает все основные данные наблюдаемости и направляет метрики в Prometheus, логи в Loki, а трассировки в Tempo. Grafana визуализирует данные и выполняет правила оповещений."
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    include taxiManager.alloy
    include observability.prometheus observability.loki observability.tempo observability.grafana
    autoLayout tb 300 200
}
