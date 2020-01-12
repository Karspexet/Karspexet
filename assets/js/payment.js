/* global Stripe */
function setupPayment(config) {
  if (!config || !config.payment) return

  var stripeKey = config.payment
  var clientSecret = config.clientSecret
  if (stripeKey === "fake") return

  if (typeof Stripe == "undefined") return

  var stripe = Stripe(stripeKey)
  var elements = stripe.elements({ locale: "sv" })

  var card = elements.create("card", {
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
  })
  card.mount("#card-element")

  var paymentForm = document.getElementById("payment-form")
  var submitButton = document.querySelector(".fn-payment-submit-button")
  var spinner = Spinner(paymentForm.querySelector(".spinner-container"))

  function setError(result) {
    var errorElement = document.querySelector(".error")
    errorElement.classList.remove("visible")
    if (result.error) {
      errorElement.textContent = result.error.message
      errorElement.classList.add("visible")
    }
    spinner.hide()
    submitButton.disabled = false
  }

  paymentForm.addEventListener("submit", function(e) {
    if (paymentForm.getAttribute("data-is-free")) {
      return
    }
    e.preventDefault()
    submitButton.disabled = true

    var paymentDetails = getStripePaymentDetails(paymentForm, card)
    spinner.show()
    stripe.confirmCardPayment(clientSecret, paymentDetails).then(function(result) {
      // Handle result.error or result.paymentIntent
      if (window.DEBUG) {
        console.debug(result)
      }
      if (result.error) {
        setError(result)
      }
      if (result.paymentIntent) {
        // FIXME: Poll for finalized reservation before redirecting to success page (show error after ~1min)
        setTimeout(function() {
          window.location.href = window.config.successUrl
        }, 5000)
      }
    })
  })

  var discountButton = document.getElementById("enter-discount-code")
  var discountForm = document.querySelector("#discount-form")
  var cancelDiscountButton = discountForm.querySelector("#cancel-discount")
  function displayDiscountForm() {
    if (discountForm.dataset.discountCode === "") {
      discountForm.classList.remove("hidden")
      discountForm.hidden = false
      discountButton.hidden = true
      paymentForm.hidden = true
    }
  }
  function closeDiscountForm() {
    discountButton.hidden = false
    discountForm.hidden = true
    paymentForm.hidden = false
  }
  if (discountButton) {
    discountButton.addEventListener("click", displayDiscountForm)
  }
  cancelDiscountButton.addEventListener("click", closeDiscountForm)
}

function getStripePaymentDetails(form, card) {
  var billing = {
    name: form.name.value,
    phone: form.phone.value,
    email: form.email.value,
  };

  var metadata = {
    reference: form.reference.value
  };
  if (!billing.phone) {
    // "phone" is not required, but Stripe doesn't want us sending
    // empty strings to them
    delete billing["phone"]
  }
  return {
    payment_method: {
      card: card,
      billing_details: billing,
      metadata: metadata,
    },
  }
}

function Spinner(elm) {
  // Wrapper to make sure we don't flash the spinner if an error
  // message is going to be shown right after we "show" the spinner
  var showTimer = null
  return {
    show: function() {
      showTimer = setTimeout(function() {
        elm.classList.remove("hidden")
      }, 50)
    },
    hide: function() {
      clearTimeout(showTimer)
      elm.classList.add("hidden")
    },
  }
}

!(function(window) {
  window.setupPayment = setupPayment
})(window)
