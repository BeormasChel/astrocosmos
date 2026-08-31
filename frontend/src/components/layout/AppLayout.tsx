import { NavLink, Outlet } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Дашборд" },
  { to: "/devices", label: "Комплексы" },
  { to: "/scenarios", label: "Сценарии" },
  { to: "/content", label: "Контент" },
  { to: "/schedule", label: "Расписание" },
  { to: "/observatory", label: "Обсерватория" },
];

/**
 * Каркас админки: боковое меню и область страницы.
 */
export function AppLayout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="logo">Астрокосмос</h1>
        <nav>
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
