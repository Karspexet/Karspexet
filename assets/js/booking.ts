import $ from "cash-dom";

export function setupBookingOverview() {
  $("[data-fn-session-timeout]").each((_, elm) => {
    const $elm = $(elm);
    let outputElement = $elm.find("[data-fn-session-timeout-output]");
    let timeElement = $elm.find("time");
    let timeout = new Date(timeElement.data("time"));
    function update() {
      const minutesRemaining = minutesUntil(timeout);
      outputElement.text(`(${minutesRemaining} minuter kvar)`);
    }
    update();
    setInterval(update, 10 * 1000);
  });
}

function minutesUntil(until: Date) {
  let now = new Date();
  let timeRemaining = (+until - +now) / 1000;
  return Math.max(0, Math.floor(timeRemaining / 60));
}
