systemLandscape "RuntimeWithObservability" {
    title "Taxi-manager и контур наблюдаемости"
    description "Показывает программные системы времени выполнения без CI/CD и без детализации внутренних контейнеров."
    include developer telemetryClient locationIq taxiManager notificationSystem observability
    autoLayout lr 320 230
}

container observability "ObservabilityContainers" {
    title "Контейнеры наблюдаемости Taxi-manager"
    description "Показывает сбор метрик, логов, трассировок и профилей. Taxi-manager раскрыт только до контейнеров, являющихся источниками телеметрии."
    include developer
    include taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.database taxiManager.varnish
    include observability.alloy observability.prometheus observability.loki observability.tempo observability.pyroscope observability.grafana observability.cadvisor observability.nginxExporter observability.varnishExporter observability.goAccess
    autoLayout tb 330 220
}
