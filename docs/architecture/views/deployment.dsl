deployment taxiManager demoEnvironment "DemoDeployment" {
    title "Развёртывание демонстрационной версии"
    description "Минимальная конфигурация docker-compose.demo.yaml: Входной веб-шлюз, Синхронное Django-приложение через uWSGI и База данных PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment taxiManager jenkinsDeploymentEnvironment "JenkinsDeployment" {
    title "Актуальное развёртывание через Jenkins"
    description "Фактически разворачиваемые контейнеры приложения. Контейнеры приложения обновляются образом успешно проверенной сборки, постоянный том PostgreSQL сохраняется. Django-контейнер наследует make run-dev из compose.jenkins-ci.yaml; Асинхронное Django-приложение и Высокопроизводительный API пока не включены в это развёртывание."
    include *
    autoLayout tb 300 220
}

deployment taxiManager targetRuntimeEnvironment "TargetRuntimeDeployment" {
    title "Целевое расширенное развёртывание"
    description "Целевая конфигурация без наблюдаемости: Синхронное и Асинхронное Django-приложения, Фоновый обработчик заданий, Высокопроизводительный API, кеши, Пул соединений, Документация API и База данных PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment * ciCdDeploymentEnvironment "CiCdDeployment" {
    title "CI/CD и развёртывание Taxi-manager"
    description "Упрощённое представление физического размещения CI/CD. GitHub Actions разворачивает и обновляет постоянный Jenkins SSH Agent. Jenkins-контроллер назначает агенту этапы основного pipeline, а агент собирает и тестирует приложение, затем обновляет Compose-проект taxi-manager-deploy с сохранением постоянного тома PostgreSQL."
    include *
    autoLayout lr 300 220
}
