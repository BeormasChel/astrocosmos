import type { ReactNode } from "react";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  lead: string;
  action?: ReactNode;
}

/**
 * Единая шапка страницы: зачем экран и одно главное действие.
 */
export function PageHeader({ eyebrow, title, lead, action }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        {eyebrow ? <p className="page-header__eyebrow">{eyebrow}</p> : null}
        <h1 className="page-header__title">{title}</h1>
        <p className="page-header__lead">{lead}</p>
      </div>
      {action ? <div className="page-header__action">{action}</div> : null}
    </header>
  );
}
