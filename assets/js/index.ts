import { setupBookingOverview } from "./booking";
import { setupPayment } from "./payment";
import { setupSelectSeats } from "./seats";
import "./number-input";

declare global {
  interface Window {
    config: any;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const { config } = window;
  if (config) {
    setupSelectSeats(config);
    setupPayment(config);
  }
  setupBookingOverview();
});
