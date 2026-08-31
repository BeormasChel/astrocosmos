import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "../api/client";
import { useAuthStore, type AuthUser } from "../stores/authStore";

interface LoginResponse {
  access_token: string;
  user: AuthUser;
}

/**
 * Вход в пульт: крупные поля, демо-учётки на локальном стенде.
 */
export function LoginPage() {
  const navigate = useNavigate();
  const setSession = useAuthStore((state) => state.setSession);
  const [login, setLogin] = useState("educator");
  const [password, setPassword] = useState("educator");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setPending(true);
    try {
      const response = await apiClient.post<LoginResponse>("/auth/login", {
        login,
        password,
      });
      setSession(response.data.access_token, response.data.user);
      navigate("/", { replace: true });
    } catch {
      setError("Не получилось войти. Проверьте логин и что ядро запущено.");
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="login">
      <form className="login__card" onSubmit={onSubmit}>
        <p className="login__brand">Астрокосмос</p>
        <h1 className="login__title">Пульт педагога</h1>
        <p className="login__lead">
          Войдите, чтобы запустить занятие в зале. Пароли стенда можно сменить
          позже в настройках.
        </p>
        <label className="login__field">
          Логин
          <input
            value={login}
            onChange={(event) => setLogin(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label className="login__field">
          Пароль
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>
        {error ? <p className="login__error">{error}</p> : null}
        <button className="btn btn--primary" type="submit" disabled={pending}>
          {pending ? "Входим…" : "Войти"}
        </button>
        <p className="login__hint">
          Стенд: педагог <strong>educator</strong> / смотритель{" "}
          <strong>attendant</strong> / администратор <strong>admin</strong>
          — пароль совпадает с логином.
        </p>
      </form>
    </div>
  );
}
