// frontend/src/App.tsx
import { Routes, Route } from "react-router-dom"
import LoginPage from "./pages/LoginPage"
import ProtectedRoute from "./components/ProtectedRoute"
import Dashboard from "./pages/Dashboard"

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="*" element={<LoginPage />} />  {/* important fallback */}
    </Routes>
  )
}