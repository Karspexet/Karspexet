import $ from "cash-dom";

export function initNumberInput(elm: HTMLInputElement) {
  function dispatchChange() {
    elm.dispatchEvent(new Event("change"));
  }

  const decrButton = $("<button type='button'>")
    .text("➖")
    .on("click", () => {
      elm.stepDown();
      dispatchChange();
    });

  const incrButton = $("<button type='button'>")
    .text("➕")
    .on("click", () => {
      elm.stepUp();
      dispatchChange();
    });

  function checkBounds() {
    decrButton.prop("disabled", !!(elm.min && elm.value <= elm.min));
    incrButton.prop("disabled", !!(elm.max && elm.value >= elm.max));
  }

  elm.addEventListener("input", checkBounds);
  elm.addEventListener("change", checkBounds);

  const wrapper = $("<span class='number-input'>");
  $(elm).replaceWith(wrapper);
  wrapper.append(decrButton, elm, incrButton);

  checkBounds();
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll<HTMLInputElement>(".fn-number-input").forEach((elm) => {
    initNumberInput(elm);
  });
});
