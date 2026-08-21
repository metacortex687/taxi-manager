styles {
    element "Element" {
        background #1168bd
        color #ffffff
        stroke #0b4884
        strokeWidth 2
        shape RoundedBox
    }

    element "Person" {
        background #08427b
        color #ffffff
        shape Person
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
        shape Cylinder
    }

    element "Auxiliary" {
        background #6b7280
        color #ffffff
    }

    element "Observability" {
        background #00695c
        color #ffffff
    }

    element "CI/CD" {
        background #5b3f8c
        color #ffffff
    }

    element "Current" {
        stroke #0b4884
        strokeWidth 3
        border solid
    }

    element "Implemented Not Deployed" {
        stroke #7c3aed
        strokeWidth 4
        border dashed
    }

    element "Prototype" {
        background #d97706
        color #ffffff
        stroke #92400e
        strokeWidth 4
        border dashed
    }

    element "Target Optional" {
        stroke #6b7280
        strokeWidth 4
        border dotted
    }

    element "Experimental" {
        background #be185d
        color #ffffff
        stroke #831843
        strokeWidth 4
        border dotted
    }

    element "Wide API" {
        width 600
    }

    element "Deployment Node" {
        background #e5e7eb
        color #111827
        stroke #6b7280
        strokeWidth 2
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

    relationship "File Mount" {
        color #6b7280
        thickness 2
        style dashed
    }

    relationship "Optional Path" {
        color #6b7280
        thickness 2
        style dashed
    }

    relationship "Experimental Flow" {
        color #be185d
        thickness 2
        style dotted
    }
}
