/**
 * Подсказка, что зелёные карточки — это стенд без Raspberry Pi.
 */
export function StandNotice({ visible }: { visible: boolean }) {
  if (!visible) {
    return null;
  }
  return (
    <div className="notice">
      <p>
        Учебный стенд: комплексы показываются «на связи» без экранов в зале. Когда
        подключим Raspberry Pi, эту подсказку уберём.
      </p>
    </div>
  );
}
