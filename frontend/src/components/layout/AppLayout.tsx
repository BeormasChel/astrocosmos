import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useHealth } from "../../hooks/useHealth";
import { useAuthStore } from "../../stores/authStore";

const NAV_ITEMS = [
  { to: "/", label: "Обзор", hint: "Что происходит", end: true },
  { to: "/lessons", label: "Занятия", hint: "Запуск для группы" },
  { to: "/complexes", label: "Комплексы", hint: "Экраны и часы" },
  { to: "/clocks", label: "Часы", hint: "Планетарное время" },
  { to: "/materials", label: "Материалы", hint: "Ролики, тексты, метки" },
  { to: "/schedule", label: "Расписание", hint: "Когда включится само" },
];

const ROLE_LABEL: Record<string, string> = {
  admin: "Администратор",
  educator: "Педагог",
  attendant: "Смотритель",
};

/**
 * Оболочка админки: короткие подписи, кто вошёл, статус ядра.
 */
export function AppLayout() {
  const health = useHealth();
  const user = useAuthStore((state) => state.user);
  const clearSession = useAuthStore((state) => state.clearSession);
  const navigate = useNavigate();
  const coreOk = health?.status === "ok";

  const logout = () => {
    clearSession();
    navigate("/login", { replace: true });
  };

  return (
    <div className="shell">
      <aside className="shell__nav">
        <div className="brand">
          <p className="brand__mark">Астрокосмос</p>
          <p className="brand__sub">
            {user ? ROLE_LABEL[user.role] ?? user.full_name : "Пульт"}
          </p>
        </div>
        <nav className="nav" aria-label="Разделы">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                isActive ? "nav__item nav__item--active" : "nav__item"
              }
            >
              <span className="nav__label">{item.label}</span>
              <span className="nav__hint">{item.hint}</span>
            </NavLink>
          ))}
        </nav>
        <div className="shell__core">
          <span
            className={`core-dot ${coreOk ? "core-dot--ok" : "core-dot--off"}`}
          />
          {coreOk ? "Ядро на связи" : "Ядро не отвечает"}
        </div>
        <button type="button" className="btn btn--ghost" onClick={logout}>
          Выйти
        </button>
      </aside>
      <main className="shell__main">
        <Outlet />
      </main>
    </div>
  );
}
