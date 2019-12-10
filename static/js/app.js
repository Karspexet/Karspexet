"use strict"
import { setupSelectSeats } from './select_seats'
import { setupBookingOverview } from './booking_overview'
import { setupPayment } from './payment'
import '../css/main.css'

(function setup(window, document) {
  function initApplication(config) {
    setupSelectSeats(config)
    setupPayment(config)
    setupBookingOverview(config)
  }

  function bootstrap(event) {
    var readyState = event.target.readyState
    switch (readyState) {
      case "complete":
        initApplication(window.config)
        break
    }
  }

  document.addEventListener("readystatechange", bootstrap)
})(window, document)
