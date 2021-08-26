declare var DEBUG: boolean;
declare var Stripe: (key: string) => {
  elements: (config: any) => any;
  confirmCardPayment: (clientSecret: any, paymentDetails: any) => any;
};

type Config = {
  successUrl: string;
  payment: string;
  clientSecret: any;
};

function q<T extends HTMLElement = HTMLElement>(selector: string): T {
  return document.querySelector<T>(selector)!;
}

export function setupPayment(config?: Config) {
  if (!config || !config.payment) return;

  let paymentForm = q<HTMLFormElement>("#payment-form")!;
  setupDiscountForm(paymentForm);

  let stripeKey = config.payment;
  let clientSecret = config.clientSecret;
  if (stripeKey === "fake") return;

  if (typeof Stripe == "undefined") return;

  let stripe = Stripe(stripeKey);
  let elements = stripe.elements({ locale: "sv" });

  let card = elements.create("card", {
    hidePostalCode: true,
    style: {
      base: {
        iconColor: "#666EE8",
        color: "#31325F",
        lineHeight: "40px",
        fontWeight: 300,
        /* eslint-disable-next-line quotes */
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSize: "15px",

        "::placeholder": {},
      },
    },
  });
  card.mount("#card-element");

  let submitButton = q<HTMLButtonElement>(".fn-payment-submit-button")!;
  let spinner = Spinner(paymentForm);

  function setError(result: { error: { message: string } }) {
    let errorElement = document.querySelector(".error")!;
    errorElement.classList.remove("visible");
    if (result.error) {
      errorElement.textContent = result.error.message;
      errorElement.classList.add("visible");
    }
    spinner.hide();
    submitButton.disabled = false;
  }

  paymentForm.addEventListener("submit", (e) => {
    if (paymentForm.getAttribute("data-is-free")) {
      return;
    }
    e.preventDefault();
    submitButton.disabled = true;

    let paymentDetails = getStripePaymentDetails(paymentForm, card);
    spinner.show();
    stripe.confirmCardPayment(clientSecret, paymentDetails).then((result: any) => {
      // Handle result.error or result.paymentIntent
      if (DEBUG) {
        console.debug(result);
      }
      if (result.error) {
        setError(result);
      }
      if (result.paymentIntent) {
        // FIXME: Poll for finalized reservation before redirecting to success page (show error after ~1min)
        setTimeout(() => {
          window.location.href = config.successUrl;
        }, 5000);
      }
    });
  });
}

function setupDiscountForm(paymentForm: HTMLFormElement) {
  let discountForm = q<HTMLFormElement>("#discount-form")!;
  let discountButton = q<HTMLButtonElement>("#enter-discount-code");
  let cancelDiscountButton = discountForm.querySelector<HTMLButtonElement>("#cancel-discount");
  if (discountButton && cancelDiscountButton) {
    discountButton.addEventListener("click", () => {
      if (discountForm.dataset.discountCode === "") {
        discountForm.classList.remove("hidden");
        discountForm.hidden = false;
        discountButton.hidden = true;
        paymentForm.hidden = true;
      }
    });
    cancelDiscountButton.addEventListener("click", () => {
      discountButton.hidden = false;
      discountForm.hidden = true;
      paymentForm.hidden = false;
    });
  }
}

function getStripePaymentDetails(form: HTMLFormElement, card: HTMLElement) {
  let billing = {
    // @ts-expect-error
    name: form.name.value,
    phone: form.phone.value,
    email: form.email.value,
  };

  let metadata = {
    reference: form.reference.value,
  };

  if (!billing.phone) {
    // "phone" is not required, but Stripe doesn't want us sending
    // empty strings to them
    delete billing["phone"];
  }
  return {
    payment_method: {
      card: card,
      billing_details: billing,
      metadata: metadata,
    },
  };
}

function Spinner(container: HTMLElement) {
  // Wrapper to make sure we don't flash the spinner if an error
  // message is going to be shown right after we "show" the spinner
  let elm = container.querySelector(".spinner-container")!;
  let showTimer: number = 0;
  return {
    show() {
      showTimer = setTimeout(() => elm.classList.remove("hidden"), 50);
    },
    hide() {
      clearTimeout(showTimer);
      elm.classList.add("hidden");
    },
  };
}
