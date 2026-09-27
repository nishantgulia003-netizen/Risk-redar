import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import Dashboard from "./pages/Dashboard";
import RiskZones from "./pages/RiskZones";
import EvacuationRoute from "./pages/EvacuationRoute";
import Shelters from "./pages/Shelters";
import AIAssistant from "./pages/AIAssistant";
import IncidentReport from "./pages/IncidentReport";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        {/* Core Emergency Command Routes with Canonical & Backward-Compatible Aliases */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/overview" element={<Navigate to="/dashboard" replace />} />
        
        <Route path="/risk-zones" element={<RiskZones />} />
        
        <Route path="/safe-evacuation-route" element={<EvacuationRoute />} />
        <Route path="/evacuation" element={<Navigate to="/safe-evacuation-route" replace />} />
        
        <Route path="/shelters" element={<Shelters />} />
        
        <Route path="/field-incident-report" element={<IncidentReport />} />
        <Route path="/reports" element={<Navigate to="/field-incident-report" replace />} />
        
        <Route path="/ai-decision-assistant" element={<AIAssistant />} />
        <Route path="/ai-assistant" element={<Navigate to="/ai-decision-assistant" replace />} />
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
