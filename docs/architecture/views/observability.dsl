systemLandscape "RuntimeWithObservability" {
    title "Taxi-manager и Платформа наблюдаемости"
    description "Показывает Taxi-manager со встроенным Коллектором наблюдаемости, внешнюю Платформу наблюдаемости и доставку email-оповещений Специалисту сопровождения без CI/CD и подсистемы уведомлений менеджеров."
    include telemetryClient locationIq taxiManager observability mailService supportSpecialist
    autoLayout lr 320 230
}

container taxiManager "ObservabilityContainers" {
    title "Основная логическая архитектура со стеком телеметрии"
    description "Встроенный в Taxi-manager Коллектор наблюдаемости Grafana Alloy собирает все основные данные наблюдаемости и направляет метрики в Prometheus, логи в Loki, а трассировки в Tempo. Grafana визуализирует данные, выполняет правила оповещений и отправляет email Специалисту сопровождения через Почтовый сервис."
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    include taxiManager.alloy
    include observability.prometheus observability.loki observability.tempo observability.grafana
    include mailService supportSpecialist
    exclude alloyToObservability
    autoLayout tb 300 200
}
