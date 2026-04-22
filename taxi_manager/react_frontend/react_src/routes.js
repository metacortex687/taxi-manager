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
    }
}

export default routes