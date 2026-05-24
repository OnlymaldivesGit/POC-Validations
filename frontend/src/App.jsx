import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RunValidator from './pages/RunValidator'
import Reports from './pages/Reports'
import Vendors from './pages/Vendors'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="run"       element={<RunValidator />} />
        <Route path="reports"   element={<Reports />} />
        <Route path="vendors"   element={<Vendors />} />
      </Route>
    </Routes>
  )
}
