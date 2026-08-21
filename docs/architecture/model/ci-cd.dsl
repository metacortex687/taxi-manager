sourceRepository = softwareSystem "Репозиторий Taxi-manager" {
    description "GitHub-репозиторий хранит исходный код приложения, Jenkinsfile, Dockerfile, compose.jenkins-ci.yaml, compose.deploy.yaml и архитектурную документацию; разработчики работают с ним через Git."
    tags "External System"
}

githubActions = softwareSystem "GitHub Actions" {
    description "Разворачивает и обновляет постоянный Jenkins-агент; не выполняет основной pipeline приложения."
    tags "External System,CI/CD"
}

containerRegistry = softwareSystem "Реестры контейнеров" {
    description "Docker Hub и Microsoft Container Registry предоставляют базовые и тестовые Docker-образы, включая образы Playwright."
    tags "External System"
}

jenkins = softwareSystem "CI/CD Taxi-manager" {
    description "Автоматизирует сборку, проверки, тестирование и развёртывание приложения. Конфигурация контроллера и агента хранится в отдельном репозитории jenkins-config."
    tags "CI/CD"

    controller = container "Jenkins-контроллер" {
        description "Создаёт job taxi-manager-ci через JCasC и Job DSL, получает Jenkinsfile, распределяет этапы pipeline и проверяет трассировки на возможные N+1-запросы."
        technology "Jenkins, JCasC, Job DSL, JDK 21"
        tags "CI/CD"
    }

    agent = container "Jenkins-агент" {
        description "Клонирует код и файлы Compose, собирает нумерованный образ, запускает изолированное CI-окружение, выполняет Django- и Playwright-тесты и после успешных проверок обновляет приложение."
        technology "Jenkins SSH Agent, JDK 21, Docker CLI, Buildx, Docker Compose"
        tags "CI/CD"
    }
}

jenkins.controller -> sourceRepository "Получает Jenkinsfile с описанием pipeline" "Git/SSH"
jenkins.controller -> jenkins.agent "Назначает этапы сборки" "Jenkins Remoting over SSH"
jenkins.agent -> sourceRepository "Клонирует исходный код, Dockerfile и файлы Compose для CI и CD" "Git/SSH"
jenkins.agent -> containerRegistry "Получает базовые и тестовые образы" "Docker Registry API"
jenkins.agent -> taxiManager "Собирает и тестирует нумерованный образ, затем пересоздаёт контейнеры приложения с сохранением тома базы данных" "Docker, Docker Compose"
jenkins.controller -> observability.tempo "Ищет трассировки с признаками N+1" "Tempo HTTP API, TraceQL"
githubActions -> jenkins.agent "Разворачивает и обновляет агент на удалённом сервере" "SSH, Docker Compose"
