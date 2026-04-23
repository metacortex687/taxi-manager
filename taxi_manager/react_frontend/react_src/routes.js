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
    vehicles: {
        path: "/enterprises/:enterprise_id/vehicles/",
        url: (enterprise_id) => `/enterprises/${enterprise_id}/vehicles/`,
        api: (enterprise_id) => `/api/v1/enterprises/${enterprise_id}/vehicles/`,
    },
    trips: {
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