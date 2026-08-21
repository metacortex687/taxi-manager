systemLandscape "CiCdLandscape" {
    title "CI/CD, наблюдаемость и Taxi-manager"
    description "Показывает отдельный от эксплуатационного C1 CI/CD-контур: репозиторий с Jenkinsfile и файлами Compose, GitHub Actions, Jenkins, приложение, Платформу наблюдаемости и внешние реестры."
    include sourceRepository githubActions containerRegistry jenkins taxiManager observability
    autoLayout lr 340 230
}

container jenkins "CiCdContainers" {
    title "C2 — Диаграмма контейнеров CI/CD Taxi-manager"
    description "Основной pipeline выполняется Jenkins. Контроллер получает Jenkinsfile, агент клонирует исходный код и файлы Compose для CI и CD; GitHub Actions используется только для развёртывания постоянного Jenkins-агента."
    include sourceRepository githubActions containerRegistry taxiManager observability.tempo
    include jenkins.controller jenkins.agent
    autoLayout lr 320 220
}

dynamic jenkins "CiCdPipeline" {
    title "Основной Jenkins pipeline"
    description "Последовательность сборки, тестирования, проверки трассировок и развёртывания. После успешных проверок контейнеры приложения обновляются образом текущей сборки, а постоянный том PostgreSQL сохраняется."
    1: jenkins.controller -> sourceRepository "Получает Jenkinsfile с описанием pipeline"
    2: jenkins.controller -> jenkins.agent "Назначает этапы сборки"
    3: jenkins.agent -> sourceRepository "Клонирует код, Dockerfile и файлы Compose для CI и CD"
    4: jenkins.agent -> containerRegistry "Получает базовые и тестовые образы"
    5: jenkins.agent -> taxiManager "Собирает нумерованный образ и запускает изолированное CI-окружение"
    6: jenkins.controller -> observability.tempo "Проверяет трассировки тестов на возможные N+1-запросы"
    7: jenkins.agent -> taxiManager "Обновляет контейнеры проверенным образом, сохраняя том базы данных"
    autoLayout lr 300 200
}
