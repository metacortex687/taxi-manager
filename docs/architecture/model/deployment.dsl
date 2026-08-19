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
