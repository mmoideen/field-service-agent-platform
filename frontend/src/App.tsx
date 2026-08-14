import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TicketsPage from './pages/TicketsPage';
import WarrantyPage from './pages/WarrantyPage';
import PartsPage from './pages/PartsPage';
import AgentActivityPage from './pages/AgentActivityPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tickets" element={<TicketsPage />} />
        <Route path="/warranty" element={<WarrantyPage />} />
        <Route path="/parts" element={<PartsPage />} />
        <Route path="/agents" element={<AgentActivityPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
