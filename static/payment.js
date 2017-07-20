/* global Stripe */
function setupPayment(stripeKey) {
    var stripe = Stripe(stripeKey)
    var elements = stripe.elements({locale: "sv"})

    var card = elements.create("card", {
        hidePostalCode: true,
        style: {
            base: {
                iconColor: "#666EE8",
                color: "#31325F",
                lineHeight: "40px",
                fontWeight: 300,
                fontFamily: "\"Helvetica Neue\", Helvetica, sans-serif",
                fontSize: "15px",

                "::placeholder": {}
            }
        }
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
        var extraDetails = {
            name: paymentForm.querySelector("input[name=name]").value
        }
        stripe.createToken(card, extraDetails).then(setOutcome)
    })
}
