function qAll(selector: string) {
  return Array.prototype.slice.call(document.querySelectorAll(selector));
}

export function setupBookingOverview() {
  qAll(".fn-session-timeout").forEach((element) => {
    let timeElement = element.querySelector("time");
    let outputElement = element.querySelector(".fn-session-timeout-output");
    setInterval(() => {
      let now = new Date();
      let timeout = new Date(timeElement.dataset.time);
      let timeRemaining = (+timeout - +now) / 1000;
      let secondsRemaining = Math.floor(timeRemaining) % 60;
      let minutesRemaining = Math.floor(timeRemaining / 60);

      outputElement.innerHTML = minutesRemaining + " minuter och " + secondsRemaining + " sekunder";
    }, 1000);
  });
}
