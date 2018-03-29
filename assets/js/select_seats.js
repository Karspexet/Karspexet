function setupSelectSeats(config) {
    if (!config || !config.seatSelection) return

    config = config.seatSelection
    var booking = {}

    var isMobile = /Mobi/.test(navigator.userAgent)

    function selectSeat(event) {
        var seat = event.target.id
        if (booking.hasOwnProperty(seat)) {
            removeSeat(seat)
        } else {
            addSeat(seat)
        }
    }

    function addSeat(seat) {
        var seatId = seat.replace("seat-", ""),
            seatElement = document.querySelector("#" + seat),
            classes = seatElement.getAttribute("class")
        booking[seat] = {id: seatId, value: null}

        seatElement.setAttribute("class", classes + " selected-seat")
        renderBooking()
    }

    function removeSeat(seat) {
        delete booking[seat]
        var seatElement = document.querySelector("#" + seat),
            classes = seatElement.getAttribute("class"),
            newClasses = classes.split(" ").filter(function(x) { return x != "selected-seat"}).join(" ")

        seatElement.setAttribute("class", newClasses)
        renderBooking()
    }

    function selectSeatType(event) {
        var target = event.target,
            seatId = target.dataset.id,
            seatType = target.value,
            seatKey = "seat-" + seatId

        booking[seatKey].value = seatType
        renderBooking()
    }

    function renderBooking() {
        var output = ""
        if (Object.keys(booking).length === 0) {
            document.querySelector("#no-seats-selected").hidden = false
            document.querySelector("#book-submit-button").disabled = true
        } else {
            document.querySelector("#book-submit-button").disabled = false
            document.querySelector("#no-seats-selected").hidden = true
            Object.keys(booking).forEach(function(seatId) {
                output += renderSeatForm(booking[seatId])
            })
        }
        document.querySelector("#booking").innerHTML = output
        Array.prototype.forEach.call(
            document.querySelectorAll("#booking select"),
            function (select) { select.addEventListener("change", selectSeatType) }
        )
    }

    function renderSeatForm(seat) {
        var seatId = seat.id,
            seatType = seat.value,
            seatObject = config.allSeats["seat-" + seatId],
            displayName = seatObject.name,
            pricing = config.pricings[seatObject.group]

        function option(seatType, selectedSeatType) {
            var selectedString = seatType === selectedSeatType ? " selected" : ""
            return [
                "<option value=\"", seatType, "\" ", selectedString, ">",
                seatType[0].toUpperCase(), seatType.slice(1),
                " (", pricing[seatType], "kr)",
                "</option>"
            ].join("")
        }
        return [
            "<div><label>", displayName, ": ",
            "<select name=\"seat_", seatId, "\" data-id=\"", seatId, "\">",
            "<option value=\"\">(Välj biljettyp)</option>",
            option("normal", seatType),
            option("student", seatType),
            "</select></label></div>"
        ].join("")
    }

    Object.keys(config.allSeats).forEach(function(seat) {
        if (isMobile) return

        var element = document.getElementById(seat),
            seatObject = config.allSeats[seat]
        element.addEventListener("mouseover", function() {
            var pricing = config.pricings[seatObject.group],
                info = [
                    "<div>", seatObject.name, "<br>",
                    "Student: ", pricing["student"], "kr", "<br>",
                    "Normal: ", pricing["normal"], "kr", "<br>",
                    "</div>"
                ].join("")

            document.querySelector(".seat-info").innerHTML = info
        })

        element.addEventListener("mouseout", function() {
            document.querySelector(".seat-info").innerHTML = ""
        })
    })

    Array.prototype.forEach.call(
        document.querySelectorAll(".seat:not(.taken-seat)"),
        function makeSeatAvailable(seat) {seat.addEventListener("click", selectSeat)}
    )
}

exports.setupSelectSeats = setupSelectSeats
