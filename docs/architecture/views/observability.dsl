systemLandscape "RuntimeWithObservability" {
    title "Taxi-manager и контур наблюдаемости"
    description "Показывает Taxi-manager и подключённый к нему контур наблюдаемости без CI/CD и подсистемы уведомлений."
    include telemetryClient locationIq taxiManager observability
    autoLayout lr 320 230
}

container taxiManager "ObservabilityContainers" {
    title "Основная логическая архитектура со стеком телеметрии"
    description "Alloy собирает телеметрию Taxi-manager и направляет метрики в Prometheus, логи в Loki, трассировки в Tempo. Grafana визуализирует данные; Pyroscope подключается опционально."
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    include observability.alloy observability.prometheus observability.loki observability.tempo observability.grafana observability.pyroscope
    autoLayout tb 300 200
}
