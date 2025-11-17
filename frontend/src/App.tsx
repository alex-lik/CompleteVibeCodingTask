import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { WebSocketProvider } from './context/WebSocketContext'
import Layout from './components/Layout'
import ProjectsPage from './pages/ProjectsPage'
import ProjectDetailPage from './pages/ProjectDetailPage'
import TasksPage from './pages/TasksPage'
import StatisticsPage from './pages/StatisticsPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  // Опции для WebSocket подключения
  const wsOptions = {
    enableNotifications: true,
    reconnectAttempts: 5,
    reconnectInterval: 3000,
    pingInterval: 30000,
  }

  return (
    <WebSocketProvider options={wsOptions}>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<ProjectsPage />} />
            <Route path="projects/:projectName" element={<ProjectDetailPage />} />
            <Route path="tasks" element={<TasksPage />} />
            <Route path="statistics" element={<StatisticsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
        <Toaster position="top-right" />
      </div>
    </WebSocketProvider>
  )
}

export default App