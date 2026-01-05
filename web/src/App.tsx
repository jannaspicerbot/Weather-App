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
    <Dashboard />
  );
}

export default App;
