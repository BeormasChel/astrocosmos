import { create } from "zustand";
import { persistToken, readStoredToken } from "../api/client";

export interface AuthUser {
  login: string;
  full_name: string;
  role: string;
}

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  setSession: (token: string, user: AuthUser) => void;
  clearSession: () => void;
}

/**
 * Сессия педагога: токен в localStorage, профиль в памяти.
 */
export const useAuthStore = create<AuthState>((set) => ({
  token: readStoredToken(),
  user: null,
  setSession: (token, user) => {
    persistToken(token);
    set({ token, user });
  },
  clearSession: () => {
    persistToken(null);
    set({ token: null, user: null });
  },
}));
