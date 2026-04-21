import { createRoot } from "react-dom/client"
import App from "./App.jsx"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000, // 1 минута без лишних перезапросов
    },
  },
})


const root = createRoot(document.getElementById("react-root"))
root.render(
  <QueryClientProvider client={queryClient}>
    <App />
  </QueryClientProvider>
)