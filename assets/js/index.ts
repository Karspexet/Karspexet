import { setupBookingOverview } from "./booking";
import { setupPayment } from "./payment";
import { setupSelectSeats } from "./seats";
import "./number-input";

declare var config: any;

document.addEventListener("DOMContentLoaded", () => {
  setupSelectSeats(config);
  setupPayment(config);
  setupBookingOverview();
});
