import TopNavbar from "./components/TopNavbar"
import AppLayout from "./components/AppLayout"
import AuthProvider from "./auth/AuthProvider"
import LoginPage from "./pages/LoginPage"
import HelloWorldPage from "./pages/HelloWorldPage"
import EnterprisesPage from "./pages/EnterprisesPage"
import RequireAuth from "./auth/RequireAuth"

import { BrowserRouter, Routes, Route } from "react-router-dom"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000, // 1 минута без лишних перезапросов
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
              <Route path="/login" element={<LoginPage />} />
              <Route element={<RequireAuth/>}>
                <Route index element={<HelloWorldPage />} /> 
                <Route path="enterprises" element={<EnterprisesPage/>} />             
              </Route>            
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App