from django_assets import Bundle, register

js = Bundle(
    "js/payment.js",
    "js/select_seats.js",
    "js/booking_overview.js",
    "js/app.js",
    filters="rjsmin",
    output="static/app-%(version)s.js",
)
css = Bundle(
    Bundle(
        "css/karspexet.css",
        "css/select_seats.css",
        "css/menu.css",
        "css/payment.css",
    ),
    Bundle(
        "css/fonts.css",
        "css/icons.css",
    ),
    filters="cssmin",
    output="static/style-%(version)s.css",
)

register("js_all", js)
register("css_all", css)
