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
        deployedCompose = deploymentNode "taxi-manager-deploy" "Compose-проект развёрнутого приложения" "Docker Compose" {
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
            containerInstance taxiManager.varnish
            containerInstance taxiManager.nginx
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
    jenkinsControllerHost = deploymentNode "Хост Jenkins-контроллера" "Узел, на котором работает Jenkins-контроллер (master)" "Linux, Docker" {
        jenkinsControllerRuntime = deploymentNode "Jenkins controller" "Контейнер управления основным pipeline Taxi-manager" "Docker Compose" {
            containerInstance jenkins.controller
        }
    }

    jenkinsAgentHost = deploymentNode "Сервер Jenkins-агента и приложения" "Удалённый Docker-хост, на котором постоянный SSH-агент выполняет сборку, тесты и развёртывание" "Linux, Docker" {
        jenkinsAgentRuntime = deploymentNode "Jenkins SSH agent" "Постоянный агент Jenkins с доступом к Docker Engine" "Docker Compose" {
            containerInstance jenkins.agent
        }

        ciCdApplicationCompose = deploymentNode "taxi-manager-deploy" "Compose-проект, обновляемый Jenkins-агентом после успешных проверок" "Docker Compose" {
            containerInstance taxiManager.nginx
            containerInstance taxiManager.djangoWsgi
            containerInstance taxiManager.taskWorker
            containerInstance taxiManager.swaggerUi
            containerInstance taxiManager.database
        }
    }
}
