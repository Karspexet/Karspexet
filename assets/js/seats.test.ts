import $ from "cash-dom";
import { expect, it } from "vitest";

import { setupFreeSeating } from "./free-seating";

it("Renders ticket selection inputs", () => {
  document.body.innerHTML = "<div data-fn-ticket-type-list></div>";
  setupFreeSeating({
    allSeats: false,
    pricings: { normal: 200, sponsor: 100, student: 300 },
  });

  expect(document.body.innerHTML).to.contain("Guldbiljett");
  expect($("input[type=number]").length).to.equal(3);

  expect(document.body.innerHTML).not.to.contain("Totalsumma");
  $($("button")[1]).trigger("click");
  expect(document.body.innerHTML).to.contain("Totalsumma");
});
