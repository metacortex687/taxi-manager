import dayjs from "dayjs"

const convertDate = (value, addDays = 0) =>
    dayjs(value).startOf('day').add(addDays, 'day').format('YYYY-MM-DDTHH:mm:ssZ')

const routes = {
    index: {
        path: "/",
        url: () => "/",        
    },
    login: {
        path: "/login",
        url: () => "/login",        
    },
    enterprises: {
        path: "/enterprises",
        url: () => "/enterprises",
        api: () => `/api/v1/enterprises/`,        
    },
    reports: {
        path: "/reports",
        url: () => "/reports",
        api: () => `/api/v1/reports/list/`,
    },
    report: {
        path: "/reports/:report_type/",
        url: (report_type) => `/reports/${report_type}/`,
    },
    enterpriseEdit: {
        path: "/enterprises/:enterprise_id/edit/",
        url: (enterprise_id) => `/enterprises/${enterprise_id}/edit/`,
        api: (enterprise_id) => `/api/v1/enterprises/${enterprise_id}/`,
    },
    vehicles: {
        path: "/enterprises/:enterprise_id/vehicles/",
        url: (enterprise_id) => `/enterprises/${enterprise_id}/vehicles/`,
        api: (enterprise_id) => `/api/v1/enterprises/${enterprise_id}/vehicles/`,
    },
    vehicleEdit: {
        path: "/vehicles/:vehicle_id/edit/",
        url: (vehicle_id) => `/vehicles/${vehicle_id}/edit/`,
        api: (vehicle_id) => `/api/v1/vehicles/${vehicle_id}/`,
    },
    trips: {
        link_name: "Маршруты",
        path: "/vehicles/:vehicle_id/trips/",
        url: (vehicle_id) => `/vehicles/${vehicle_id}/trips/`,
        api: {
            list: (vehicle_id, dateFrom, dateTo) => {
                const params = new URLSearchParams()

                if (dateFrom) {
                    params.set("from", convertDate(dateFrom))
                }

                if (dateTo) {
                    params.set("to", convertDate(dateTo, 1))
                }

                return `/api/v1/vehicles/${vehicle_id}/trips/?${params.toString()}`
            },
            points: (vehicle_id, dateFrom, dateTo) => {
                const params = new URLSearchParams({
                    response_format: "geojson",
                })

                if (dateFrom) {
                    params.set("from", convertDate(dateFrom))
                }

                if (dateTo) {
                    params.set("to", convertDate(dateTo, 1))
                }

                return `/api/v1/vehicles/${vehicle_id}/trip-points/?${params.toString()}`
        },
    },
        export:{
            path: "/enterprises/:enterprise_id/export/trips/",
            url: (enterprise_id) => `/enterprises/${enterprise_id}/export/trips/`,
            api: (enterprise_id, dateFrom, dateTo) => {
                const params = new URLSearchParams({
                    from: convertDate(dateFrom),
                    to: convertDate(dateTo,1),
                })
                return `/api/v1/enterprises/${enterprise_id}/export/trips/?${params.toString()}`
            },
        },
        import: {
            path: "/enterprises/:enterprise_id/import/trips/",
            url: (enterprise_id) => `/enterprises/${enterprise_id}/import/trips/`,
            api: (enterprise_id, fileName) =>
                `/api/v1/enterprises/${enterprise_id}/import/trips/${encodeURIComponent(fileName)}/`,
        },
    }
}

export default routes