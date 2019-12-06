function disableSubmitButton() {
  document.querySelector("#no-seats-selected").hidden = false
  document.querySelector("#book-submit-button").disabled = true
}

function enableSubmitButton() {
  document.querySelector("#book-submit-button").disabled = false
  document.querySelector("#no-seats-selected").hidden = true
}

function setupSeatMapSelection(config) {
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
    booking[seat] = { id: seatId, value: null }

    seatElement.setAttribute("class", classes + " selected-seat")
    renderBooking()
  }

  function removeSeat(seat) {
    delete booking[seat]
    var seatElement = document.querySelector("#" + seat),
      classes = seatElement.getAttribute("class"),
      newClasses = classes
        .split(" ")
        .filter(function(x) {
          return x != "selected-seat"
        })
        .join(" ")

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
      disableSubmitButton()
    } else {
      enableSubmitButton()
      Object.keys(booking).forEach(function(seatId) {
        output += renderSeatForm(booking[seatId])
      })
    }
    document.querySelector("#booking").innerHTML = output
    Array.prototype.forEach.call(document.querySelectorAll("#booking select"), function(select) {
      select.addEventListener("change", selectSeatType)
    })
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
        '<option value="',
        seatType,
        '" ',
        selectedString,
        ">",
        seatType[0].toUpperCase(),
        seatType.slice(1),
        " (",
        pricing[seatType],
        "kr)",
        "</option>",
      ].join("")
    }
    return [
      "<div><label>",
      displayName,
      ": ",
      '<select name="seat_',
      seatId,
      '" data-id="',
      seatId,
      '">',
      '<option value="">(Välj biljettyp)</option>',
      option("normal", seatType),
      option("student", seatType),
      "</select></label></div>",
    ].join("")
  }

  Object.keys(config.allSeats).forEach(function(seat) {
    if (isMobile) return

    var element = document.getElementById(seat),
      seatObject = config.allSeats[seat]
    element.addEventListener("mouseover", function() {
      var pricing = config.pricings[seatObject.group],
        info = [
          "<div>",
          seatObject.name,
          "<br>",
          "Student: ",
          pricing["student"],
          "kr",
          "<br>",
          "Fullpris: ",
          pricing["normal"],
          "kr",
          "<br>",
          "</div>",
        ].join("")

      document.querySelector(".seat-info").innerHTML = info
    })

    element.addEventListener("mouseout", function() {
      document.querySelector(".seat-info").innerHTML = ""
    })
  })

  Array.prototype.forEach.call(
    document.querySelectorAll(".seat:not(.taken-seat)"),
    function makeSeatAvailable(seat) {
      seat.addEventListener("click", selectSeat)
    },
  )
}

function setupFreeSeating(config) {
  var booking = {
    student: 0,
    normal: 0,
  }

  function setNumberOfSeats(seatType, numberOfSeats) {
    var saneNumberOfSeats = Number(numberOfSeats) < 0 ? 0 : Number(numberOfSeats)
    booking[seatType] = saneNumberOfSeats
  }

  function renderBooking() {
    var bookingElement = document.getElementById("booking")
    if (booking.student === 0 && booking.normal === 0) {
      disableSubmitButton()
      bookingElement.innerText = ""

      return
    }

    enableSubmitButton()
    var studentTotal = (booking.student || 0) * (config.pricings.student || 0)
    var normalTotal = (booking.normal || 0) * (config.pricings.normal || 0)
    var totalPrice = studentTotal + normalTotal
    bookingElement.innerText = "Totalsumma: " + totalPrice
  }

  function setupChangeNumberOfSeats(seatType) {
    return function changeSeats(event) {
      var numberOfSeats = Number(event.target.value)
      if (numberOfSeats < 0) {
        numberOfSeats = 0
      }

      setNumberOfSeats(seatType, numberOfSeats)
      renderBooking()
    }
  }

  var numberOfSeatsElements = document.getElementsByClassName("number-of-seats")
  Array.prototype.forEach.call(numberOfSeatsElements, function setupEventListeners(field) {
    var seatType = field.getAttribute("name")
    setNumberOfSeats(seatType, field.value)
    if (typeof field.value !== "number") {
      field.value = 0
    }
    renderBooking()
    field.addEventListener("change", setupChangeNumberOfSeats(seatType))
  })
}

function setupSelectSeats(config) {
  if (!config || !config.seatSelection) return
  config = config.seatSelection

  if (config.freeSeating) {
    return setupFreeSeating(config)
  } else {
    return setupSeatMapSelection(config)
  }
}

!(function(window) {
  window.setupSelectSeats = setupSelectSeats
})(window)
