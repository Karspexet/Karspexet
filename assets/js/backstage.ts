import Tablesort from "tablesort";

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-tablesort]").forEach((el) => {
    Tablesort(el, {});
  });
});
