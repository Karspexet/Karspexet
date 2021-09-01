import $, { Cash } from "cash-dom";

declare var DEBUG: boolean;
declare var Stripe: (key: string) => {
  elements: (config: any) => any;
  confirmCardPayment: (clientSecret: any, paymentDetails: any) => any;
};

type Config = {
  successUrl: string;
  stripeKey: string;
  clientSecret: any;
};

export function setupPayment(config: Config) {
  const { stripeKey, clientSecret } = config;

  let paymentForm = $("#payment-form")!;
  setupDiscountForm(paymentForm);

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

  let submitButton = $(".fn-payment-submit-button")!;
  let spinner = Spinner(paymentForm);

  function setError(result: { error: { message: string } }) {
    let errorElement = $(".error")!;
    errorElement.removeClass("visible");
    if (result.error) {
      errorElement.text(result.error.message);
      errorElement.addClass("visible");
    }
    spinner.hide();
    submitButton.prop("disabled", false);
  }

  paymentForm.on("submit", (e) => {
    if (paymentForm.attr("data-is-free")) {
      return;
    }
    e.preventDefault();
    submitButton.prop("disabled", true);

    let paymentDetails = getStripePaymentDetails(paymentForm.get(0) as HTMLFormElement, card);
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

function setupDiscountForm(paymentForm: Cash) {
  let discountForm = $("#discount-form")!;
  let discountButton = $("#enter-discount-code");
  let cancelDiscountButton = discountForm.find("#cancel-discount");
  discountButton.on("click", () => {
    if (discountForm.data("discountCode") === "") {
      discountForm.removeClass("hidden");
      discountForm.show();
      discountButton.hide();
      paymentForm.hide();
    }
  });
  cancelDiscountButton.on("click", () => {
    discountButton.show();
    discountForm.hide();
    paymentForm.show();
  });
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

function Spinner(container: Cash) {
  // Wrapper to make sure we don't flash the spinner if an error
  // message is going to be shown right after we "show" the spinner
  let elm = container.find(".spinner-container")!;
  const showTimer = timeout(() => elm.removeClass("hidden"));
  return {
    show() {
      showTimer.queue(50);
    },
    hide() {
      showTimer.cancel();
      elm.addClass("hidden");
    },
  };
}

function timeout(func: Function) {
  let timer: number = 0;
  return {
    queue: (t: number) => {
      setTimeout(func, t);
    },
    cancel: () => {
      clearTimeout(timer);
    },
  };
}
