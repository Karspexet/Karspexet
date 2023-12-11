import $ from "cash-dom";

import { setupFreeSeating } from "./free-seating";

type PriceConfig = {
  seatSelection: SeatSelection;
};

export type SeatSelection = {
  allSeats: any;
  freeSeating?: any;
  pricings: Record<string, null | number>;
};

export function setupSelectSeats(config: PriceConfig) {
  const { seatSelection } = config || {};
  if (!seatSelection) return;

  if (seatSelection.freeSeating) {
    return setupFreeSeating(seatSelection);
  } else {
    return setupSeatMapSelection(seatSelection);
  }
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
        selected: seatType === selectedSeatType,
        textContent: seatTypeTitle + " (" + pricing[seatType] + "kr)",
        value: seatType,
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
          children: [selectElm],
          textContent: displayName + ": ",
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
          createElm("div", { textContent: "Rabatterad: " + pricing["student"] + "kr" }),
          createElm("div", { textContent: "Ordinarie: " + pricing["normal"] + "kr" }),
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

function disableSubmitButton() {
  $("#book-submit-button").prop("disabled", true);
}

function enableSubmitButton() {
  $("#book-submit-button").prop("disabled", false);
}
