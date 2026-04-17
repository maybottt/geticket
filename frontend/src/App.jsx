import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@features/auth/context/AuthContext'
import PrivateRoute from '@features/auth/routes/PrivateRoute'
import LoginPage from '@features/auth/pages/LoginPage'
import SwitchRolPage from '@features/auth/pages/SwitchRolPage'
import DashboardPage from '@features/dashboard/pages/DashboardPage'
import TicketDetailPage from '@features/tickets/pages/TicketDetailPage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/switch-rol" element={
            <PrivateRoute><SwitchRolPage /></PrivateRoute>
          } />
          <Route path="/dashboard" element={
            <PrivateRoute><DashboardPage /></PrivateRoute>
          } />
          <Route path="/tickets/:id" element={
            <PrivateRoute><TicketDetailPage /></PrivateRoute>
          } />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}