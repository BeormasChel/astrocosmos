import axios from "axios";

/** HTTP-клиент к ядру `/api/v1`. */
export const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 10_000,
});

const TOKEN_KEY = "astrocosmos.token";

/**
 * Прочитать сохранённый JWT.
 */
export function readStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Запомнить или сбросить JWT.
 */
export function persistToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

apiClient.interceptors.request.use((config) => {
  const token = readStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = String(error.config?.url ?? "");
    if (error.response?.status === 401 && !url.includes("/auth/login")) {
      persistToken(null);
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  },
);
