systemLandscape "RuntimeWithObservability" {
    title "Taxi-manager и Платформа наблюдаемости"
    description "Показывает основное приложение со встроенным Коллектором наблюдаемости, внешнюю Платформу наблюдаемости и доставку email-оповещений Специалисту сопровождения. CI/CD и Система уведомлений менеджеров не показаны."
    include telemetryClient locationIq taxiManager observability mailService supportSpecialist
    autoLayout lr 320 230
}

container taxiManager "ObservabilityContainers" {
    title "C2 — Диаграмма контейнеров наблюдаемости Taxi-manager"
    description "Grafana Alloy получает трассировки приложений по OTLP, собирает метрики через Prometheus scrape и читает журналы контейнеров, затем направляет метрики в Prometheus, логи в Loki, а трассировки в Tempo. Grafana визуализирует данные, выполняет правила оповещений и отправляет email Специалисту сопровождения через Почтовый сервис."
    include taxiManager.webUi taxiManager.nginx taxiManager.djangoWsgi taxiManager.djangoAsgi taxiManager.taskWorker taxiManager.rustApi taxiManager.database taxiManager.swaggerUi
    include taxiManager.alloy
    include observability.prometheus observability.loki observability.tempo observability.grafana
    include mailService supportSpecialist
    exclude alloyToObservability
    autoLayout tb 300 200
}
