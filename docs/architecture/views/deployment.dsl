deployment taxiManager demoEnvironment "DemoDeployment" {
    title "Развёртывание демонстрационной версии"
    description "Минимальная конфигурация docker-compose.demo.yaml: Входной веб-шлюз, Синхронный REST API через uWSGI и База данных PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment taxiManager jenkinsDeploymentEnvironment "JenkinsDeployment" {
    title "Актуальное развёртывание через Jenkins"
    description "Фактически разворачиваемые контейнеры приложения. Контейнеры приложения обновляются образом успешно проверенной сборки, постоянный том PostgreSQL сохраняется. Синхронный REST API наследует make run-dev из compose.jenkins-ci.yaml; Асинхронный REST API и SSE и Высокопроизводительный асинхронный REST API пока не включены в это развёртывание."
    include *
    autoLayout tb 300 220
}

deployment taxiManager targetRuntimeEnvironment "TargetRuntimeDeployment" {
    title "Целевое расширенное развёртывание"
    description "Целевая конфигурация без наблюдаемости: Синхронный REST API, Асинхронный REST API и SSE, Фоновый обработчик заданий, Высокопроизводительный асинхронный REST API, Сервис авторизации, кэши, Пул соединений, Документация API и База данных PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment * ciCdDeploymentEnvironment "CiCdDeployment" {
    title "CI/CD и развёртывание Taxi-manager"
    description "Упрощённое представление физического размещения CI/CD. GitHub Actions разворачивает и обновляет Jenkins-агент. Jenkins-мастер назначает агенту этапы конвейера CI/CD, а агент собирает и тестирует приложение, затем обновляет Compose-проект taxi-manager-deploy с сохранением постоянного тома PostgreSQL."
    include *
    autoLayout lr 300 220
}

