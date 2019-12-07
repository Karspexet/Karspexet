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

  function setOutcome(result) {
    var errorElement = document.querySelector(".error")
    errorElement.classList.remove("visible")

    if (result.token) {
      stripeTokenHandler(result.token)
    } else if (result.error) {
      errorElement.textContent = result.error.message
      errorElement.classList.add("visible")
    }
  }

  card.on("change", function(event) {
    setOutcome(event)
  })

  function showSpinner() {
    paymentForm.querySelector(".spinner-container").classList.remove("hidden")
  }

  function hideSpinner() {
    paymentForm.querySelector(".spinner-container").classList.add("hidden")
  }

  function disableSubmit() {
    var button = document.querySelector(".fn-payment-submit-button")
    button.disabled = true
  }

  function enableSubmit() {
    var button = document.querySelector(".fn-payment-submit-button")
    button.disabled = false
  }

  function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var form = document.getElementById("payment-form")
    var hiddenInput = document.createElement("input")
    hiddenInput.setAttribute("type", "hidden")
    hiddenInput.setAttribute("name", "stripeToken")
    hiddenInput.setAttribute("value", token.id)
    form.appendChild(hiddenInput)

    // Submit the form
    form.submit()
  }
  var paymentForm = document.getElementById("payment-form")
  paymentForm.addEventListener("submit", function(e) {
    e.preventDefault()
    var billing = {
      name: paymentForm.name.value,
      phone: paymentForm.phone.value,
      email: paymentForm.email.value,
    }
    disableSubmit()
    showSpinner()
    stripe
      .confirmCardPayment(clientSecret, {
        payment_method: {
          card: card,
          billing_details: billing,
        },
      })
      .then(function(result) {
        // Handle result.error or result.paymentIntent
        if (result.error) {
          setPaymentError(result.error.message)
          hideSpinner()
          enableSubmit()
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

function setPaymentError(message) {
  // FIXME: This has no styling
  var err = document.getElementById("fn-payment-errors")
  err.innerHTML = null
  err.appendChild(createWarning("Något gick fel, betalningen gick inte igenom."))
  err.appendChild(createWarning(message))
}

function createWarning(text) {
  var elm = document.createElement("div")
  elm.textContent = text
  return elm
}

!(function(window) {
  window.setupPayment = setupPayment
})(window)
