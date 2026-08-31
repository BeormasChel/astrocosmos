import { useEffect, useMemo, useState } from "react";

import {
  fetchIlluminatorWindow,
  HEARTBEAT_MS,
  POLL_MS,
  sendIlluminatorHeartbeat,
  type IlluminatorClip,
  type IlluminatorWindow as WindowState,
} from "./api";

/**
 * Полноэкранное окно: ролик занятия или Attract Mode.
 */
export function IlluminatorWindow() {
  const hideCursor = useMemo(
    () => new URLSearchParams(window.location.search).has("kiosk"),
    [],
  );
  const [state, setState] = useState<WindowState | null>(null);
  const [attractIndex, setAttractIndex] = useState(0);

  useEffect(() => {
    const ping = async () => {
      try {
        await sendIlluminatorHeartbeat();
      } catch {
        // Зал может быть без ядра: окно остаётся чёрным, Attract с кэша — позже.
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
        const next = await fetchIlluminatorWindow();
        if (!cancelled) {
          setState(next);
        }
      } catch {
        // Держим последний кадр, пока ядро не ответит.
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

  const mode = state?.mode ?? "attract";
  const attract = state?.attract ?? [];

  const clip: IlluminatorClip | null = useMemo(() => {
    if (mode === "play") {
      return state?.clip ?? null;
    }
    if (attract.length === 0) {
      return state?.clip ?? null;
    }
    return attract[attractIndex % attract.length] ?? null;
  }, [attract, attractIndex, mode, state?.clip]);

  const showVideo = Boolean(clip?.hasFile && clip.videoUrl);
  const showCaption = Boolean(clip && !clip.hasFile);

  /**
   * В Attract переключаем ролик после конца файла.
   */
  const handleEnded = () => {
    if (mode !== "attract" || attract.length < 2) {
      return;
    }
    setAttractIndex((current) => current + 1);
  };

  const className = hideCursor ? "viewport viewport--kiosk" : "viewport";

  return (
    <div className={className}>
      {showVideo && clip?.videoUrl ? (
        <video
          key={clip.videoUrl}
          className="viewport__video"
          src={clip.videoUrl}
          autoPlay
          muted
          playsInline
          loop={mode === "play"}
          onEnded={handleEnded}
        />
      ) : (
        <div className="starfield" aria-hidden="true">
          <div className="starfield__layer starfield__layer--far" />
          <div className="starfield__layer starfield__layer--mid" />
          <div className="starfield__layer starfield__layer--near" />
        </div>
      )}
      {showCaption ? <p className="viewport__caption">{clip?.title}</p> : null}
    </div>
  );
}
