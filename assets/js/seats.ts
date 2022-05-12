import $ from "cash-dom";

import { initNumberInput } from "./number-input";

const SPONSOR_TYPE = "sponsor";

type PriceConfig = {
  seatSelection: SeatSelection;
};
type SeatSelection = {
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

function disableSubmitButton() {
  $("#book-submit-button").prop("disabled", true);
}

function enableSubmitButton() {
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

export function setupFreeSeating(config: SeatSelection) {
  let booking = createBookingState(config);

  const requiredFields = $("[data-select-seats-form]").find("[required]");
  requiredFields.on("input", renderBooking);

  const totalElm = $('<div class="mt-4"></div>');
  const listElm = $("<ul>");
  $("[data-fn-ticket-type-list]").append(listElm, totalElm);

  function renderBooking() {
    const hasTickets = booking.getTotalTicketCount() > 0;
    totalElm.text(!hasTickets ? "" : `Totalsumma: ${booking.getTotalPrice()} SEK`);

    if (hasTickets && !!requiredFields.val()) {
      enableSubmitButton();
    } else {
      disableSubmitButton();
    }
  }
  const luva = createHappyLuva();

  const types = ["sponsor", "normal", "student"];
  for (let price of types) {
    listElm.append(TicketInputRow(price, config.pricings as any));
  }

  listElm
    .find("input[type=number]")
    .each((_, elm) => {
      initNumberInput(elm as HTMLInputElement);
    })
    .each((_, elm: any) => {
      let seatType = elm.getAttribute("name");
      elm.value = elm.value || 0;
      booking.setTicketCount(seatType, elm.value);
      elm.addEventListener("change", () => {
        booking.setTicketCount(seatType, elm.value);
        renderBooking();

        if (seatType === SPONSOR_TYPE) {
          luva.dance();
        }
      });
    });

  renderBooking();
}

function createBookingState(config: SeatSelection) {
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

  function getTotalTicketCount() {
    let sum = 0;
    for (let price in booking) {
      sum += booking[price];
    }
    return sum;
  }

  function setTicketCount(seatType: string, value: number) {
    booking[seatType] = Math.max(Number(value), 0);
  }

  return {
    getTotalPrice,
    getTotalTicketCount,
    setTicketCount,
  };
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

const titles: { [k: string]: string } = {
  normal: "Fullpris",
  sponsor: "Guldbiljett",
  student: "Student",
};

function TicketInputRow(type: string, pricings: { [k: string]: number }) {
  const title = titles[type];
  const price = pricings[type];
  return $("<li>").append(
    $('<div class="flex h-16 items-center">').append(
      $('<div class="mr-2 ticket-name">').append(
        $('<strong class="text-lg">').text(title),
        $("<div>").text(price + " SEK"),
      ),
      $('<input type="number" class="number-of-seats" min="0">').attr("name", type),
    ),
    SponsorTicketMessage(type, pricings),
  );
}

function SponsorTicketMessage(type: string, pricings: { [k: string]: number }) {
  const sponsorPrice = pricings["sponsor"];
  const normalPrice = pricings["normal"];
  if (type !== "sponsor" || !sponsorPrice || !normalPrice) {
    return null;
  }
  const extra = sponsorPrice - normalPrice;
  const msgRows = [
    // fmt: expand
    `Guldbiljetten sponsrar oss med ${extra} kr,`,
    "stort tack för din gåva!",
  ];
  return $('<div class="flex gap-2 ml-2 max-w-sm">').append(
    $("<img data-sponsor-luva>")
      .attr("src", "/static/svg/luva.svg")
      .attr("alt", "")
      .attr("class", "luva"),
    $("<em>").append(...msgRows.map((text) => $('<span class="block">').text(text))),
  );
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
  img.on("animationend", (_) => {
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
