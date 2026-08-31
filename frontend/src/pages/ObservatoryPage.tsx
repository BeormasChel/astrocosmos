import { PageHeader } from "../components/PageHeader";

/**
 * Обсерватория сознательно не в главном меню.
 */
export function ObservatoryPage() {
  return (
    <section className="page">
      <PageHeader
        title="Обсерватория"
        lead="Купол и Vizor живут в своём комплексе «Диптих» и на своём MQTT. Сейчас из зала нужен только видеопоток на Астровизор. Общий пульт спроектируем, когда будет API."
      />
      <div className="empty">
        <p className="empty__title">Раздел откроем позже</p>
        <p>
          Астровизор (экран в зале) и Vizor (датчик угла купола) — разные
          устройства. Их нельзя перепутать в настройках.
        </p>
      </div>
    </section>
  );
}
