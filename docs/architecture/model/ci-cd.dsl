sourceRepository = softwareSystem "Репозиторий Taxi-manager" {
    description "GitHub-репозиторий хранит исходный код приложения, Jenkinsfile, Dockerfile, Docker Compose и архитектурную документацию; разработчики работают с ним через Git."
    tags "External System"
}

githubActions = softwareSystem "GitHub Actions" {
    description "Разворачивает и обновляет постоянный Jenkins-агент; не выполняет основной pipeline Taxi-manager."
    tags "External System,CI/CD"
}

containerRegistry = softwareSystem "Реестры контейнеров" {
    description "Docker Hub и Microsoft Container Registry предоставляют базовые и тестовые Docker-образы, включая образы Playwright."
    tags "External System"
}

jenkins = softwareSystem "CI/CD Taxi-manager" {
    description "Автоматизирует сборку, проверки, тестирование и развёртывание Taxi-manager. Конфигурация контроллера и агента хранится в отдельном репозитории jenkins-config."
    tags "CI/CD"

    controller = container "Jenkins-контроллер" {
        description "Хранит конфигурацию pipeline, создаёт job taxi-manager-ci, распределяет этапы и выполняет проверку трассировок на возможные N+1-запросы."
        technology "Jenkins, JCasC, Job DSL, JDK 21"
        tags "CI/CD"
    }

    agent = container "Jenkins-агент" {
        description "Клонирует код, собирает образы, запускает тестовые окружения, выполняет Django- и Playwright-тесты и разворачивает приложение."
        technology "Jenkins SSH Agent, JDK 21, Docker CLI, Buildx, Docker Compose"
        tags "CI/CD"
    }
}

developer -> sourceRepository "Публикует изменения" "Git/SSH"
jenkins.controller -> sourceRepository "Получает Jenkinsfile и описание pipeline" "Git/SSH"
jenkins.controller -> jenkins.agent "Назначает этапы сборки" "Jenkins Remoting over SSH"
jenkins.agent -> sourceRepository "Клонирует исходный код" "Git/SSH"
jenkins.agent -> containerRegistry "Получает базовые и тестовые образы" "Docker Registry API"
jenkins.agent -> taxiManager "Собирает, тестирует и разворачивает приложение" "Docker, Docker Compose"
jenkins.controller -> observability.tempo "Ищет трассировки с признаками N+1" "Tempo HTTP API, TraceQL"
jenkins.controller -> observability "Использует трассировки тестового окружения для проверки N+1" "Tempo HTTP API, TraceQL"
githubActions -> jenkins.agent "Разворачивает и обновляет агент на удалённом сервере" "SSH, Docker Compose"
