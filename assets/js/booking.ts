import $ from "cash-dom";

export function setupBookingOverview() {
  $(".fn-session-timeout").each((i, element) => {
    let timeElement = $("time");
    let outputElement = $(".fn-session-timeout-output");
    setInterval(() => {
      let now = new Date();
      let timeout = new Date(timeElement.data("time"));
      let timeRemaining = (+timeout - +now) / 1000;
      let minutesRemaining = Math.floor(timeRemaining / 60);

      outputElement.text(minutesRemaining + " minuter");
    }, 1000);
  });
}
