function toPositive(x: any) {
  x = Number(x);
  return Math.max(x, 0);
}

function qAll(selector: string) {
  return Array.prototype.slice.call(document.querySelectorAll(selector));
}

function disableSubmitButton() {
  document.querySelector<HTMLElement>("#no-seats-selected")!.hidden = false;
  document.querySelector<HTMLButtonElement>("#book-submit-button")!.disabled = true;
}

function enableSubmitButton() {
  document.querySelector<HTMLElement>("#no-seats-selected")!.hidden = true;
  document.querySelector<HTMLButtonElement>("#book-submit-button")!.disabled = false;
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
    let seatElement = document.querySelector("#" + seat)!;
    let classes = seatElement.getAttribute("class");
    booking[seat] = { id: seatId, value: null };

    seatElement.setAttribute("class", classes + " selected-seat");
    renderBooking();
  }

  function removeSeat(seat: string) {
    delete booking[seat];
    let seatElement = document.querySelector("#" + seat)!;
    let classes = seatElement.getAttribute("class")!;
    let newClasses = classes
      .split(" ")
      .filter((x) => x != "selected-seat")
      .join(" ");

    seatElement.setAttribute("class", newClasses);
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
    document.querySelector("#booking")!.innerHTML = output;
    qAll("#booking select").forEach((select) => {
      select.addEventListener("change", selectSeatType);
    });
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

    let seatInfoElm = document.querySelector(".seat-info")!;
    let element = document.getElementById(seat)!;
    let seatObject = config.allSeats[seat];
    element.addEventListener("mouseover", () => {
      let pricing = config.pricings[seatObject.group];

      let info = createElm("div", {
        children: [
          createElm("div", { textContent: seatObject.name }),
          createElm("div", { textContent: "Student: " + pricing["student"] + "kr" }),
          createElm("div", { textContent: "Fullpris: " + pricing["normal"] + "kr" }),
        ],
      });

      seatInfoElm.innerHTML = info.outerHTML;
    });

    element.addEventListener("mouseout", () => {
      seatInfoElm.innerHTML = "";
    });
  });

  qAll(".seat:not(.taken-seat)").forEach((seat) => seat.addEventListener("click", selectSeat));
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
    let bookingElement = document.getElementById("booking")!;

    if (getTicketCount() === 0) {
      disableSubmitButton();
      bookingElement.innerText = "";
    } else {
      enableSubmitButton();
      bookingElement.innerText = "Totalsumma: " + getTotalPrice();
    }
  }

  qAll(".number-of-seats").forEach(function setupEventListeners(field) {
    let seatType = field.getAttribute("name");
    function changeSeats() {
      booking[seatType] = toPositive(field.value);
      renderBooking();
    }
    field.value = field.value || 0;
    field.addEventListener("change", changeSeats);
    changeSeats();
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
