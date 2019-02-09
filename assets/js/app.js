"use strict";

(function(window, document) {
    function initApplication(config) {
        window.setupSelectSeats(config)
        window.setupPayment(config)
        window.setupBookingOverview(config)
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
})(window, document);
