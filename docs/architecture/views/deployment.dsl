deployment taxiManager demoEnvironment "DemoDeployment" {
    title "Развёртывание демонстрационной версии"
    description "Минимальная конфигурация docker-compose.demo.yaml: Nginx, Django WSGI через uWSGI и PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment taxiManager jenkinsDeploymentEnvironment "JenkinsDeployment" {
    title "Актуальное развёртывание через Jenkins"
    description "Фактически разворачиваемые контейнеры приложения. Django-контейнер наследует make run-dev из compose.jenkins-ci.yaml; ASGI и Rust API пока не включены в этот deployment."
    include *
    autoLayout tb 300 220
}

deployment taxiManager targetRuntimeEnvironment "TargetRuntimeDeployment" {
    title "Целевое расширенное развёртывание"
    description "Целевая конфигурация без наблюдаемости: WSGI, ASGI, task worker, Rust API, кеши, пул соединений, Swagger UI и PostgreSQL/PostGIS."
    include *
    autoLayout tb 300 220
}

deployment * ciCdDeploymentEnvironment "CiCdDeployment" {
    title "CI/CD и развёртывание Taxi-manager"
    description "Jenkins-контроллер (master) назначает этапы постоянному SSH-агенту. Агент собирает и тестирует приложение, затем обновляет Compose-проект taxi-manager-deploy."
    include *
    autoLayout lr 300 220
}
