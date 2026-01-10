import { useEffect } from 'react';
import { initializeApiClient } from './lib/api-config';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  // Initialize API client on mount
  useEffect(() => {
    initializeApiClient();
  }, []);

  return (
    <>
      {/* Skip link for keyboard navigation (WCAG 2.4.1) */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      <Dashboard />
    </>
  );
}

export default App;
