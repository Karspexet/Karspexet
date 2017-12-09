function remainingTime(timeElement, outputElement) {
    var now = new Date(),
        timeout = new Date(timeElement.dataset.time),
        timeRemaining = (timeout - now) / 1000,
        secondsRemaining = Math.floor(timeRemaining) % 60,
        minutesRemaining = Math.floor(timeRemaining / 60)

    outputElement.innerHTML = minutesRemaining + " minuter och " + secondsRemaining + " sekunder"
}
function setupBookingOverview() {
    Array.prototype.forEach.call(
        document.querySelectorAll(".fn-session-timeout"),
        function (element) {
            var timeElement = element.querySelector("time"),
                outputElement = element.querySelector(".fn-session-timeout-output")
            setInterval(
                function() { remainingTime(timeElement, outputElement) },
                1000
            )
        }
    )
}

exports.setupBookingOverview = setupBookingOverview
