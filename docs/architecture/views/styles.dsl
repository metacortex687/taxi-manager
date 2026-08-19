styles {
    element "Element" {
        background #1168bd
        color #ffffff
        stroke #0b4884
        strokeWidth 2
        shape roundedbox
    }

    element "Person" {
        background #08427b
        color #ffffff
        shape person
    }

    element "External System" {
        background #767676
        color #ffffff
        stroke #555555
    }

    element "Gateway" {
        background #2b7a78
        color #ffffff
    }

    element "Worker" {
        background #438dd5
        color #ffffff
    }

    element "Database" {
        background #2e7d32
        color #ffffff
        shape cylinder
    }

    element "Auxiliary" {
        background #6b7280
        color #ffffff
    }

    element "Boundary" {
        stroke #1168bd
        strokeWidth 3
    }

    relationship "Relationship" {
        color #707070
        thickness 2
    }

    relationship "Database Access" {
        color #2e7d32
        thickness 2
    }

    relationship "External API Call" {
        color #d97706
        thickness 3
        style dashed
    }
}

