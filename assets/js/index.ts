import { setupBookingOverview } from "./booking";
import { initSentry } from "./errors";
import "./number-input";
import { setupPayment } from "./payment";
import { setupSelectSeats } from "./seats";

declare global {
  interface Window {
    config: {
      clientSecret: string;
      seatSelection: any;
      stripeKey: string;
      successUrl: string;
    };
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initSentry();

  const { config } = window;
  if (config) {
    setupSelectSeats(config);
    setupPayment(config);
  }
  setupBookingOverview();
});
