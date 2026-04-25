import TopNavbar from "./components/TopNavbar"
import AppLayout from "./components/AppLayout"
import AuthProvider from "./auth/AuthProvider"

import LoginPage from "./pages/LoginPage"
import HelloWorldPage from "./pages/HelloWorldPage"
import EnterprisesPage from "./pages/EnterprisesPage"
import EnterpriseEditPage from "./pages/EnterpriseEditPage"
import VehiclesPage from "./pages/VehiclesPage"
import VehicleEditPage from "./pages/VehicleEditPage"
import TripsExportPage from "./pages/TripsExportPage"
import TripsImportPage from "./pages/TripsImportPage"

import RequireAuth from "./auth/RequireAuth"

import '@mantine/core/styles.css'
import '@mantine/dates/styles.css'
import 'dayjs/locale/ru'
import { MantineProvider } from '@mantine/core'
import { DatesProvider } from '@mantine/dates'

import { Toaster } from 'react-hot-toast'


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
    <MantineProvider>
      <DatesProvider settings={{ locale: 'ru' }}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter basename="/react">
            <AuthProvider>
              <TopNavbar />
              <Toaster
                position="top-center"
                toastOptions={{
                  duration: 4000,
                }}
              />
              <Routes>
                <Route element={<AppLayout />}>
                  <Route path={routes.login.path} element={<LoginPage />} />
                  <Route element={<RequireAuth/>}>
                    <Route index element={<HelloWorldPage />} /> 
                    <Route path={routes.enterprises.path} element={<EnterprisesPage/>} />
                    <Route path={routes.enterpriseEdit.path} element={<EnterpriseEditPage />} /> 
                    <Route path={routes.vehicles.path} element={<VehiclesPage/>} /> 
                    <Route path={routes.vehicleEdit.path} element={<VehicleEditPage/>} />                     
                    <Route path={routes.trips.export.path} element={<TripsExportPage/>} />
                    <Route path={routes.trips.import.path} element={<TripsImportPage />} />             
                  </Route>            
                </Route>
              </Routes>
            </AuthProvider>
          </BrowserRouter>
        </QueryClientProvider>
      </DatesProvider>
    </MantineProvider>

  )
}

export default App