import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ScheduleDays from './pages/ScheduleDays'
import DayWorkspace from './pages/DayWorkspace'
import Vendors from './pages/Vendors'
import Analytics from './pages/Analytics'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/days" replace />} />
        <Route path="days"              element={<ScheduleDays />} />
        <Route path="days/:date"        element={<DayWorkspace />} />
        <Route path="days/:date/:tab"   element={<DayWorkspace />} />
        <Route path="vendors"           element={<Vendors />} />
        <Route path="analytics"         element={<Analytics />} />
        <Route path="settings"          element={<Analytics />} />
      </Route>
    </Routes>
  )
}
