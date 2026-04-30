import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Camaras from './pages/Camaras'
import Alertas from './pages/Alertas'
import Dispositivos from './pages/Dispositivos'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }/>
          <Route path="/camaras" element={
            <PrivateRoute>
              <Camaras />
            </PrivateRoute>
          }/>
          <Route path="/alertas" element={
            <PrivateRoute>
              <Alertas />
            </PrivateRoute>
          }/>
          <Route path="/dispositivos" element={
            <PrivateRoute>
              <Dispositivos />
            </PrivateRoute>
          }/>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App