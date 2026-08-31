import { create } from "zustand";

interface AuthState {
  token: string | null;
  setToken: (token: string | null) => void;
}

/**
 * Клиентское состояние сессии администратора/педагога.
 */
export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  setToken: (token) => set({ token }),
}));
