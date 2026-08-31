import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { DashboardPage } from "./pages/DashboardPage";
import { DevicesPage } from "./pages/DevicesPage";
import { ScenariosPage } from "./pages/ScenariosPage";
import { ContentPage } from "./pages/ContentPage";
import { SchedulePage } from "./pages/SchedulePage";
import { ClocksPage } from "./pages/ClocksPage";
import { ObservatoryPage } from "./pages/ObservatoryPage";
import { LoginPage } from "./pages/LoginPage";
import { AppLayout } from "./components/layout/AppLayout";
import { RequireAuth } from "./components/RequireAuth";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: 1, refetchOnWindowFocus: false },
  },
});

/**
 * Маршруты админки: вход, затем рабочие экраны педагога.
 */
export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<RequireAuth />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/lessons" element={<ScenariosPage />} />
              <Route path="/complexes" element={<DevicesPage />} />
              <Route path="/clocks" element={<ClocksPage />} />
              <Route path="/materials" element={<ContentPage />} />
              <Route path="/schedule" element={<SchedulePage />} />
              <Route path="/observatory" element={<ObservatoryPage />} />
              <Route path="/scenarios" element={<Navigate to="/lessons" replace />} />
              <Route path="/devices" element={<Navigate to="/complexes" replace />} />
              <Route path="/content" element={<Navigate to="/materials" replace />} />
            </Route>
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
