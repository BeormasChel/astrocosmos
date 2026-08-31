import { useEffect, useMemo, useState } from "react";

import {
  fetchHoloboxWindow,
  HEARTBEAT_MS,
  POLL_MS,
  sendHoloboxHeartbeat,
  type HoloboxSection,
  type HoloboxWindow,
} from "./api";

type HoloboxView = "attract" | "menu" | "section";

const DEFAULT_IDLE_MS = 60_000;

/**
 * Тач-киоск малого голобокса: Attract, меню разделов, ролик.
 */
export function MalyHolobox() {
  const hideCursor = useMemo(
    () => new URLSearchParams(window.location.search).has("kiosk"),
    [],
  );
  const [remote, setRemote] = useState<HoloboxWindow | null>(null);
  const [view, setView] = useState<HoloboxView>("attract");
  const [localSectionId, setLocalSectionId] = useState<string | null>(null);
  const [touchAt, setTouchAt] = useState(() => Date.now());

  useEffect(() => {
    document.title = "Малый Голобокс";
  }, []);

  useEffect(() => {
    const ping = async () => {
      try {
        await sendHoloboxHeartbeat();
      } catch {
        // Без ядра остаёмся на чёрном фоне — камень в витрине виден.
      }
    };
    void ping();
    const timer = window.setInterval(() => {
      void ping();
    }, HEARTBEAT_MS);
    return () => {
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const next = await fetchHoloboxWindow();
        if (!cancelled) {
          setRemote(next);
        }
      } catch {
        // Держим последнее меню, пока ядро не ответит.
      }
    };
    void poll();
    const timer = window.setInterval(() => {
      void poll();
    }, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const lessonLocked = Boolean(remote?.lessonLocked);

  useEffect(() => {
    // Занятие открывает раздел само; стоп возвращает Attract.
    if (lessonLocked) {
      setView("section");
      setLocalSectionId(null);
      return;
    }
    setView("attract");
  }, [lessonLocked]);

  const idleMs = (remote?.idleSeconds ?? 60) * 1000 || DEFAULT_IDLE_MS;

  useEffect(() => {
    if (lessonLocked || view === "attract") {
      return;
    }
    const timer = window.setTimeout(() => {
      setView("attract");
      setLocalSectionId(null);
    }, idleMs);
    return () => {
      window.clearTimeout(timer);
    };
  }, [idleMs, lessonLocked, touchAt, view]);

  const section: HoloboxSection | null = lessonLocked
    ? remote?.section ?? null
    : (remote?.sections.find((item) => item.id === localSectionId) ?? null);

  /**
   * Любое касание сбрасывает idle; с заставки сразу в меню.
   */
  const handleTouch = () => {
    setTouchAt(Date.now());
    if (!lessonLocked && view === "attract") {
      setView("menu");
    }
  };

  const openSection = (sectionId: string) => {
    setLocalSectionId(sectionId);
    setView("section");
    setTouchAt(Date.now());
  };

  const backToMenu = () => {
    if (lessonLocked) {
      return;
    }
    setLocalSectionId(null);
    setView("menu");
    setTouchAt(Date.now());
  };

  const className = hideCursor ? "holobox holobox--kiosk" : "holobox";
  const showVideo = Boolean(section?.hasFile && section.videoUrl);

  return (
    <div className={className} onPointerDown={handleTouch}>
      {view === "attract" && !lessonLocked ? (
        <div className="holobox__attract">
          <p className="holobox__eyebrow">Челябинский метеорит</p>
          <p className="holobox__cta">Коснитесь экрана</p>
        </div>
      ) : null}

      {view === "menu" && !lessonLocked ? (
        <div className="holobox__menu">
          <p className="holobox__eyebrow">Выберите раздел</p>
          <div className="holobox__grid">
            {(remote?.sections ?? []).map((item) => (
              <button
                key={item.id}
                type="button"
                className="holobox__tile"
                onClick={() => openSection(item.id)}
              >
                <span className="holobox__tile-title">{item.title}</span>
                <span className="holobox__tile-hint">{item.hint}</span>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      {view === "section" || lessonLocked ? (
        <div className="holobox__section">
          {showVideo && section?.videoUrl ? (
            <video
              key={section.videoUrl}
              className="holobox__video"
              src={section.videoUrl}
              autoPlay
              muted
              playsInline
              loop
            />
          ) : (
            <div className="holobox__caption">
              <p className="holobox__eyebrow">{section?.title ?? ""}</p>
              <p className="holobox__hint">{section?.hint ?? ""}</p>
            </div>
          )}
          {!lessonLocked ? (
            <button type="button" className="holobox__back" onClick={backToMenu}>
              Назад
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
