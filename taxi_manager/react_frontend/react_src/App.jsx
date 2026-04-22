import TopNavbar from "./components/TopNavbar"
import AppLayout from "./components/AppLayout"
import AuthProvider from "./auth/AuthProvider"

import LoginPage from "./pages/LoginPage"
import HelloWorldPage from "./pages/HelloWorldPage"
import EnterprisesPage from "./pages/EnterprisesPage"
import VehiclesPage from "./pages/VehiclesPage"

import RequireAuth from "./auth/RequireAuth"


import routes from "./routes"

import { BrowserRouter, Routes, Route } from "react-router-dom"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 10_000, // 10 секунд
    },
  },
})


function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter basename="/react">
        <AuthProvider>
          <TopNavbar />
          <Routes>
            <Route element={<AppLayout />}>
              <Route path={routes.login.path} element={<LoginPage />} />
              <Route element={<RequireAuth/>}>
                <Route index element={<HelloWorldPage />} /> 
                <Route path={routes.enterprises.path} element={<EnterprisesPage/>} /> 
                <Route path={routes.vehicles.path} element={<VehiclesPage/>} />             
              </Route>            
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App