import TopNavbar from "./components/TopNavbar"
import AppLayout from "./components/AppLayout"
import AuthProvider from "./auth/AuthProvider"
import LoginPage from "./pages/LoginPage"
import HelloWorldPage from "./pages/HelloWorldPage"
import RequireAuth from "./auth/RequireAuth"

import { BrowserRouter, Routes, Route } from "react-router-dom"


function App() {
  return (
    <BrowserRouter basename="/react">
      <AuthProvider>
        <TopNavbar />
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<RequireAuth/>}>
              <Route path="/" element={<HelloWorldPage />} />            
            </Route>            
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App