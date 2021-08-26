document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll<HTMLInputElement>(".fn-number-input").forEach((elm) => {
    const decrButton = button({ textContent: "➖" });
    const incrButton = button({ textContent: "➕" });

    const wrapper = document.createElement("span");
    wrapper.classList.add("number-input");
    elm.replaceWith(wrapper);
    wrapper.appendChild(decrButton);
    wrapper.appendChild(elm);
    wrapper.appendChild(incrButton);

    function checkBounds() {
      decrButton.disabled = !!(elm.min && elm.value <= elm.min);
      incrButton.disabled = !!(elm.max && elm.value >= elm.max);
    }
    checkBounds();
    decrButton.addEventListener("click", () => {
      elm.stepDown();
      elm.dispatchEvent(new Event("change"));
    });
    incrButton.addEventListener("click", () => {
      elm.stepUp();
      elm.dispatchEvent(new Event("change"));
    });
    elm.addEventListener("change", checkBounds);
    elm.addEventListener("input", checkBounds);
  });
});

function button({ textContent }: { textContent: string }) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.textContent = textContent;
  return btn;
}
