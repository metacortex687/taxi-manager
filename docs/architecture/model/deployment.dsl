demoEnvironment = deploymentEnvironment "Demo" {
    demoBrowser = deploymentNode "Пользовательское устройство" "Компьютер пользователя демо-версии" "Web browser" {
        containerInstance taxiManager.webUi
    }

    demoHost = deploymentNode "Локальный Docker-хост" "Компьютер с Docker Engine или Docker Desktop" "Docker" {
        demoCompose = deploymentNode "docker-compose.demo.yaml" "Минимальное демонстрационное окружение" "Docker Compose" {
            containerInstance taxiManager.nginx
            containerInstance taxiManager.djangoWsgi
            containerInstance taxiManager.database
        }
    }
}

jenkinsDeploymentEnvironment = deploymentEnvironment "Jenkins deployment" {
    deployedBrowser = deploymentNode "Пользовательское устройство" "Браузер сотрудника автопарка" "Web browser" {
        containerInstance taxiManager.webUi
    }

    deployedHost = deploymentNode "Сервер приложения" "Удалённый Docker-хост, на котором Jenkins-агент выполняет развёртывание" "Linux, Docker" {
        deployedCompose = deploymentNode "taxi-manager-deploy" "Фактически развёрнутый Compose-проект: контейнеры приложения обновляются образом проверенной сборки, а постоянный том базы данных сохраняется" "Docker Compose" {
            containerInstance taxiManager.nginx
            containerInstance taxiManager.djangoWsgi
            containerInstance taxiManager.taskWorker
            containerInstance taxiManager.swaggerUi
            containerInstance taxiManager.database
        }
    }
}

targetRuntimeEnvironment = deploymentEnvironment "Target runtime" {
    targetBrowser = deploymentNode "Пользовательское устройство" "Браузер сотрудника автопарка" "Web browser" {
        containerInstance taxiManager.webUi
    }

    targetHost = deploymentNode "Сервер приложения" "Целевой Docker-хост" "Linux, Docker" {
        targetCompose = deploymentNode "Расширенное окружение" "Целевая конфигурация приложения без стека наблюдаемости" "Docker Compose" {
            containerInstance taxiManager.nginx
            containerInstance taxiManager.authorizationService
            containerInstance taxiManager.varnish
            containerInstance taxiManager.djangoWsgi
            containerInstance taxiManager.djangoAsgi
            containerInstance taxiManager.taskWorker
            containerInstance taxiManager.rustApi
            containerInstance taxiManager.swaggerUi
            containerInstance taxiManager.pgbouncer
            containerInstance taxiManager.memcached
            containerInstance taxiManager.database
        }
    }
}

ciCdDeploymentEnvironment = deploymentEnvironment "CI/CD deployment" {
    githubHost = deploymentNode "GitHub" "Облачная инфраструктура, в которой выполняется workflow развёртывания Jenkins-агента" "GitHub" {
        githubActionsRunner = infrastructureNode "GitHub Actions" "Запускает workflow, который разворачивает и обновляет Jenkins-агент" "GitHub-hosted runner"
    }

    jenkinsControllerHost = deploymentNode "Хост Jenkins-мастера" "Узел, на котором работает Jenkins-мастер" "Linux, Docker" {
        jenkinsControllerRuntime = deploymentNode "Jenkins-мастер" "Координирует конвейер CI/CD приложения" "Docker Compose" {
            containerInstance jenkins.controller
        }
    }

    jenkinsAgentHost = deploymentNode "Сервер Jenkins-агента и приложения" "Удалённый Docker-хост, на котором Jenkins-агент выполняет сборку, тесты и развёртывание" "Linux, Docker" {
        jenkinsAgentRuntime = deploymentNode "Jenkins-агент" "Выполняет этапы конвейера CI/CD приложения с использованием Docker Engine" "Docker Compose" {
            jenkinsAgentInstance = containerInstance jenkins.agent
        }

        ciCdApplicationCompose = deploymentNode "taxi-manager-deploy" "Compose-проект, обновляемый Jenkins-агентом образом успешно проверенной сборки с сохранением постоянного тома PostgreSQL" "Docker Compose" {
            containerInstance taxiManager.nginx
            containerInstance taxiManager.djangoWsgi
            containerInstance taxiManager.taskWorker
            containerInstance taxiManager.swaggerUi
            containerInstance taxiManager.database
        }
    }

    githubHost.githubActionsRunner -> jenkinsAgentHost.jenkinsAgentRuntime.jenkinsAgentInstance "Разворачивает и обновляет Jenkins-агент" "SSH, Docker Compose"
}
