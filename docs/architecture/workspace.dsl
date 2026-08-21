workspace "Taxi-manager" "Многопредставленческая C4-модель приложения Taxi-manager, подключаемой подсистемы уведомлений менеджеров, наблюдаемости и CI/CD." {

    !identifiers hierarchical
    !impliedRelationships true

    model {
        !include model/taxi-manager.dsl
        !include model/notifications.dsl
        !include model/observability.dsl
        !include model/ci-cd.dsl
        !include model/deployment.dsl
    }

    views {
        !include views/taxi-manager.dsl
        !include views/notifications.dsl
        !include views/observability.dsl
        !include views/ci-cd.dsl
        !include views/deployment.dsl
        !include views/styles.dsl
    }

    configuration {
        scope none
    }
}
