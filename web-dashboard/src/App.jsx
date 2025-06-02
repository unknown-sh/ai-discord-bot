import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AdminDashboard from "./pages/AdminDashboard";
import AuditLog from "./pages/AuditLog";
import AuthProvider from "./components/AuthProvider";
import NavBar from "./components/NavBar";
import { ThemeProvider } from "./components/ThemeProvider";
import { ToastProvider } from "./components/Toast";
import ConfigPage from "./pages/ConfigPage";
import UsersPage from "./pages/UsersPage";
import RolesPage from "./pages/RolesPage";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    window._dashboardError = { error, errorInfo };
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ color: 'red', padding: 20 }}>
          <h2>Something went wrong in the dashboard UI.</h2>
          <pre>{this.state.error && this.state.error.toString()}</pre>
          <pre>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function WrappedApp() {
  React.useEffect(() => {
    console.log('[DEBUG] WrappedApp mounted');
    window._dashboardDebug = window._dashboardDebug || [];
    window._dashboardDebug.push({
      event: 'mount',
      time: new Date().toISOString(),
      location: 'WrappedApp',
    });
  }, []);
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <ToastProvider>
          <AuthProvider>
            <Router>
              <NavBar />
              <div style={{ fontFamily: "sans-serif", maxWidth: 900, margin: "0 auto", padding: 24 }}>
                <Routes>
                  <Route path="/admin" element={<AdminDashboard />} />
                  <Route path="/audit" element={<AuditLog />} />
                  <Route path="/config" element={<ConfigPage />} />
                  <Route path="/users" element={<UsersPage />} />
                  <Route path="/roles" element={<RolesPage />} />
                  <Route path="/" element={
                    <div style={{ padding: 32 }}>
                      <h1>AI Discord Bot Dashboard</h1>
                      <p>Welcome! This dashboard will let you manage bot config, memory, users, and more.</p>
                      <p>Use the navigation above to access admin features and audit logs.</p>
                    </div>
                  } />
                </Routes>
              </div>
            </Router>
          </AuthProvider>
        </ToastProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}


