import $ from "cash-dom";

const SPONSOR_TYPE = "sponsor";

function disableSubmitButton() {
  $("#no-seats-selected").show();
  $("#book-submit-button").prop("disabled", true);
}

function enableSubmitButton() {
  $("#no-seats-selected").hide();
  $("#book-submit-button").prop("disabled", false);
}

function setupSeatMapSelection(config: { allSeats: any; pricings: any }) {
  let booking: Record<string, { id: any; value: any }> = {};

  let isMobile = /Mobi/.test(navigator.userAgent);

  function selectSeat(event: any) {
    let seat = event.target.id;
    if (booking.hasOwnProperty(seat)) {
      removeSeat(seat);
    } else {
      addSeat(seat);
    }
  }

  function addSeat(seat: string) {
    let seatId = seat.replace("seat-", "");
    booking[seat] = { id: seatId, value: null };
    $("#" + seat).addClass("selected-seat");
    renderBooking();
  }

  function removeSeat(seat: string) {
    delete booking[seat];
    $("#" + seat).removeClass("selected-seat");
    renderBooking();
  }

  function selectSeatType(event: any) {
    let target = event.target;
    let seatId = target.dataset.id;
    let seatType = target.value;
    let seatKey = "seat-" + seatId;

    booking[seatKey].value = seatType;
    renderBooking();
  }

  function renderBooking() {
    let output = "";
    if (Object.keys(booking).length === 0) {
      disableSubmitButton();
    } else {
      enableSubmitButton();
      Object.keys(booking).forEach((seatId) => {
        output += renderSeatForm(booking[seatId]);
      });
    }
    $("#booking").html(output);
    $("#booking select").on("change", selectSeatType);
  }

  function renderSeatForm(seat: any) {
    let seatId = seat.id;
    let seatType = seat.value;
    let seatObject = config.allSeats["seat-" + seatId];
    let displayName = seatObject.name;
    let pricing = config.pricings[seatObject.group];

    function option(seatType: any, selectedSeatType: any) {
      let seatTypeTitle = seatType[0].toUpperCase() + seatType.slice(1);
      let e = createElm("option", {
        value: seatType,
        selected: seatType === selectedSeatType,
        textContent: seatTypeTitle + " (" + pricing[seatType] + "kr)",
      });
      return e.outerHTML;
    }

    let selectElm = document.createElement("select");
    selectElm.name = "seat_" + seatId;
    selectElm.setAttribute("data-id", seatId);
    selectElm.innerHTML += "<option value=''>(Välj biljettyp)</option>";
    selectElm.innerHTML += option("normal", seatType);
    selectElm.innerHTML += option("student", seatType);

    let d = createElm("div", {
      children: [
        createElm("label", {
          textContent: displayName + ": ",
          children: [selectElm],
        }),
      ],
    });
    return d.outerHTML;
  }

  Object.keys(config.allSeats).forEach((seat) => {
    if (isMobile) return;

    let seatInfoElm = $(".seat-info");
    let element = $(seat);
    const { group, name } = config.allSeats[seat];
    element.on("mouseover", () => {
      let pricing = config.pricings[group];

      let info = createElm("div", {
        children: [
          createElm("div", { textContent: name }),
          createElm("div", { textContent: "Student: " + pricing["student"] + "kr" }),
          createElm("div", { textContent: "Fullpris: " + pricing["normal"] + "kr" }),
        ],
      });

      seatInfoElm.html(info.outerHTML);
    });

    element.on("mouseout", () => {
      seatInfoElm.html("");
    });
  });

  $(".seat:not(.taken-seat)").on("click", selectSeat);
}

function setupFreeSeating(config: { pricings: any }) {
  let booking: Record<string, number> = {};
  for (let price in config.pricings) {
    booking[price] = 0;
  }

  function getTotalPrice() {
    let sum = 0;
    for (let price in booking) {
      sum += (booking[price] || 0) * (config.pricings[price] || 0);
    }
    return sum;
  }

  function getTicketCount() {
    let sum = 0;
    for (let price in booking) {
      sum += booking[price];
    }
    return sum;
  }

  function renderBooking() {
    let bookingElement = $("booking");

    if (getTicketCount() === 0) {
      disableSubmitButton();
      bookingElement.text("");
    } else {
      enableSubmitButton();
      bookingElement.text("Totalsumma: " + getTotalPrice());
    }
  }
  const luva = createHappyLuva();

  $(".number-of-seats").each((_, field: any) => {
    let seatType = field.getAttribute("name");
    function changeSeats() {
      booking[seatType] = Math.max(Number(field.value), 0);
      renderBooking();
    }
    field.value = field.value || 0;
    changeSeats();

    field.addEventListener("change", () => {
      changeSeats();

      if (seatType === SPONSOR_TYPE) {
        luva.dance();
      }
    });
  });
}

export function setupSelectSeats(config: any) {
  if (!config || !config.seatSelection) return;
  config = config.seatSelection;

  if (config.freeSeating) {
    return setupFreeSeating(config);
  } else {
    return setupSeatMapSelection(config);
  }
}

function createElm(type: any, options: any) {
  options = options || {};
  let children = options.children || [];
  delete options.children;
  let elm = document.createElement(type);
  for (let prop in options) {
    if (prop === "selected" && options[prop]) {
      elm.setAttribute(prop, "");
    } else {
      elm[prop] = options[prop];
    }
  }
  for (let i = 0, len = children.length; i < len; i++) {
    elm.appendChild(children[i]);
  }
  return elm;
}

function createHappyLuva() {
  let spins = 0;
  const img = $("[data-sponsor-luva]");
  const spinClasses = ["spin-once", "shake"];
  function animate(type?: string) {
    img.addClass(type || randomChoice(spinClasses));
    img.data("is-animated", true);
  }
  function dance() {
    spins += 1;
    if (!img.data("is-animated")) {
      animate();
    }
  }
  img.on("animationend", (e) => {
    img.data("is-animated", false);
    img.removeClass(spinClasses.join(" "));
    spins -= 1;
    if (img.hasClass("animate-fast")) {
      spins = 0;
      img.removeClass("animate-fast");
    }
    if (spins > 0) {
      img.addClass("animate-fast");
      setTimeout(() => animate("spin-once"), 0);
    }
  });
  return {
    dance,
  };
}

function randomChoice<T>(choice: T[]): T {
  var index = Math.floor(Math.random() * choice.length);
  return choice[index];
}
