import { useEffect } from 'react';
import { initializeApiClient } from './lib/api-config';
import WeatherTest from './components/WeatherTest';
import './App.css';

function App() {
  // Initialize API client on mount
  useEffect(() => {
    initializeApiClient();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <WeatherTest />
    </div>
  );
}

export default App;
