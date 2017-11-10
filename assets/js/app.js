(function(window, document) {
    var setupPayment = require("./payment.js").setupPayment,
        setupSelectSeats = require("./select_seats.js").setupSelectSeats

    function initApplication(config) {
        setupSelectSeats(config)
        setupPayment(config)
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
