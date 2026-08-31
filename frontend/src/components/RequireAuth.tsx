import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { apiClient } from "../api/client";
import { useAuthStore, type AuthUser } from "../stores/authStore";

/**
 * Пускать в пульт только с живым JWT.
 */
export function RequireAuth() {
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);
  const setSession = useAuthStore((state) => state.setSession);
  const clearSession = useAuthStore((state) => state.clearSession);
  const [checking, setChecking] = useState(Boolean(token && !user));

  useEffect(() => {
    if (!token) {
      setChecking(false);
      return;
    }
    if (user) {
      setChecking(false);
      return;
    }

    let cancelled = false;
    apiClient
      .get<AuthUser>("/auth/me")
      .then((response) => {
        if (!cancelled) {
          setSession(token, response.data);
          setChecking(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          clearSession();
          setChecking(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token, user, setSession, clearSession]);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (checking) {
    return <p className="page">Открываем пульт…</p>;
  }

  return <Outlet />;
}
