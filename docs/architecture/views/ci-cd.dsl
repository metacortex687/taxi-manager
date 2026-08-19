systemLandscape "CiCdLandscape" {
    title "CI/CD, наблюдаемость и Taxi-manager"
    description "Показывает репозиторий, GitHub Actions, Jenkins, приложение, контур наблюдаемости и внешние реестры на уровне программных систем."
    include developer sourceRepository githubActions containerRegistry jenkins taxiManager observability
    autoLayout lr 340 230
}

container jenkins "CiCdContainers" {
    title "Контейнеры CI/CD Taxi-manager"
    description "Основной pipeline выполняется Jenkins; GitHub Actions используется для развёртывания постоянного Jenkins-агента."
    include developer sourceRepository githubActions containerRegistry taxiManager observability.tempo
    include jenkins.controller jenkins.agent
    autoLayout lr 320 220
}

dynamic jenkins "CiCdPipeline" {
    title "Основной Jenkins pipeline Taxi-manager"
    description "Упрощённая последовательность сборки, тестирования, проверки трассировок и развёртывания."
    1: jenkins.controller -> sourceRepository "Получает Jenkinsfile и описание pipeline"
    2: jenkins.controller -> jenkins.agent "Назначает этапы сборки"
    3: jenkins.agent -> sourceRepository "Клонирует исходный код"
    4: jenkins.agent -> containerRegistry "Получает базовые и тестовые образы"
    5: jenkins.agent -> taxiManager "Собирает образ и запускает изолированное тестовое окружение"
    6: jenkins.controller -> observability "Проверяет трассировки тестов на возможные N+1-запросы"
    7: jenkins.agent -> taxiManager "Разворачивает проверенный образ"
    autoLayout lr 300 200
}
