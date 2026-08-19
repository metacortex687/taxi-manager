workspace "Taxi-manager" "Логическая C4-модель Taxi-manager. Работающее приложение, наблюдаемость и CI/CD описываются отдельными представлениями." {

    !identifiers hierarchical
    !impliedRelationships true

    model {
        !include model/taxi-manager.dsl
        !include model/observability.dsl
        !include model/ci-cd.dsl
    }

    views {
        !include views/taxi-manager.dsl
        !include views/observability.dsl
        !include views/ci-cd.dsl
        !include views/styles.dsl
    }

    configuration {
        scope softwaresystem
    }
}

