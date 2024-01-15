import $ from "cash-dom";

import { initNumberInput } from "./number-input";
import { SeatSelection } from "./seats";
import { randomChoice, sum } from "./utils";

const SPONSOR_TYPE = "sponsor";

const titles: { [k: string]: string } = {
  normal: "Ordinarie",
  sponsor: "Guldbiljett",
  student: "Rabatterad",
};

export function setupFreeSeating(config: SeatSelection) {
  let booking = createBookingState(config.pricings);

  const requiredFields = $("[data-select-seats-form]").find("[required]");
  requiredFields.on("input", renderBooking);

  const totalElm = $('<div class="mt-4"></div>');
  const listElm = $("<ul>");
  $("[data-fn-ticket-type-list]").append(listElm, totalElm);

  function renderBooking() {
    const hasTickets = booking.getTotalTicketCount() > 0;
    totalElm.text(!hasTickets ? "" : `Totalsumma: ${booking.getTotalPrice()} SEK`);
    const allowSubmit = hasTickets && !!requiredFields.val();
    $("#book-submit-button").prop("disabled", !allowSubmit);
  }

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
      elm.addEventListener("change", () => {
        booking.setTicketCount(seatType, elm.value);
        renderBooking();

        if (seatType === SPONSOR_TYPE) {
          document.dispatchEvent(new Event("spex:dance-luva"));
        }
      });
    });

  attachHappyLuva();

  renderBooking();
}

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
    DiscountTicketMessage(type),
  );
}

const spinClasses = ["spin-once", "shake"];

function attachHappyLuva() {
  let spins = 0;
  const img = $("[data-sponsor-luva]");
  function animate(type?: string) {
    img.addClass(type || randomChoice(spinClasses));
    img.data("is-animated", true);
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
  document.addEventListener("spex:dance-luva", function dance() {
    spins += 1;
    if (!img.data("is-animated")) {
      animate();
    }
  });
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

function DiscountTicketMessage(type: string) {
  if (type !== "student") {
    return null;
  }
  const msgRows = ["För barn under 18, studenter och pensionärer"];
  return $('<div class="flex gap-2 ml-2 max-w-sm">').append(
    $("<em>").append(...msgRows.map((text) => $('<span class="block">').text(text))),
  );
}

function createBookingState(prices: SeatSelection["pricings"]) {
  let booking: Record<string, number> = {};
  const getCount = (type: string): number => booking[type] || 0;
  const getPrice = (type: string): number => prices[type] || 0;

  return {
    getTotalPrice() {
      return sum(Object.keys(booking).map((type) => getCount(type) * getPrice(type)));
    },
    getTotalTicketCount() {
      return sum(Object.keys(booking).map(getCount));
    },
    setTicketCount(seatType: string, value: number) {
      booking[seatType] = Math.max(Number(value), 0);
    },
  };
}
