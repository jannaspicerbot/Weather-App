/**
 * Main Application Component
 * Sets up React Query and renders the Weather Dashboard
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { WeatherDashboard } from './components/WeatherDashboard';

// Create a React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <WeatherDashboard />
    </QueryClientProvider>
  );
}

export default App;
