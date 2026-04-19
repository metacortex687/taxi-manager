import TopNavbar from "./components/TopNavbar.js"
import AppLayout from "./components/AppLayout.js"
import AuthProvider from "./auth/AuthProvider.js"

function App() {  
  return (
    <AuthProvider>
      <AppLayout>
        <TopNavbar />
        <h1>Hello world !!!</h1>
      </AppLayout> 
    </AuthProvider>
  )

}

export default App