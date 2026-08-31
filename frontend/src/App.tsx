import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { ScenariosPage } from "./pages/ScenariosPage";
import { ContentPage } from "./pages/ContentPage";
import { SchedulePage } from "./pages/SchedulePage";
import { ObservatoryPage } from "./pages/ObservatoryPage";
import { AppLayout } from "./components/layout/AppLayout";

/**
 * Корневой компонент админки: маршруты разделов MVP.
 */
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/devices" element={<DevicesPage />} />
          <Route path="/scenarios" element={<ScenariosPage />} />
          <Route path="/content" element={<ContentPage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/observatory" element={<ObservatoryPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
