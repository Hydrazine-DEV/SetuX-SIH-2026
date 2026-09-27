import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/layout/Layout';

// Public Pages
import Home from './pages/Home';
import OfficerLogin from './pages/OfficerLogin';
import CitizenLogin from './pages/CitizenLogin';
import CitizenDashboard from './pages/CitizenDashboard';

// Protected Officer Pages
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import ProjectDetails from './pages/ProjectDetails';
import Analytics from './pages/Analytics';
import Risk from './pages/Risk';
import Warnings from './pages/Warnings';
import MapView from './pages/MapView';
import Issues from './pages/Issues';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <Router>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/officer-login" element={<OfficerLogin />} />
              <Route path="/citizen-login" element={<CitizenLogin />} />
              <Route path="/login" element={<Navigate to="/officer-login" replace />} />

              {/* Public Citizen Portal View */}
              <Route path="/citizen-dashboard" element={<CitizenDashboard />} />

              {/* Protected Officer Routes */}
              <Route element={<ProtectedRoute allowedRoles={['officer']} />}>
                <Route element={<Layout />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/projects" element={<Projects />} />
                  <Route path="/projects/:id" element={<ProjectDetails />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/risk" element={<Risk />} />
                  <Route path="/warnings" element={<Warnings />} />
                  <Route path="/map" element={<MapView />} />
                  <Route path="/issues" element={<Issues />} />
                  <Route path="/reports" element={<Reports />} />
                  <Route path="/settings" element={<Settings />} />

                  {/* Backward compatibility aliases */}
                  <Route path="/field-updates" element={<Navigate to="/issues" replace />} />
                  <Route path="/ai-analytics" element={<Navigate to="/risk" replace />} />
                  <Route path="/report" element={<Navigate to="/issues" replace />} />
                  <Route path="/ai-verification" element={<Navigate to="/risk" replace />} />
                </Route>
              </Route>

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

