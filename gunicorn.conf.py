# Gunicorn conf for local development
#
# Start with:
#
#   python -u -m gunicorn --reload -w 2

# logger_class = "gunicorn_color.Logger"
access_log_format = "%(m)s %(s)s %(U)s%(q)s"
accesslog = "-"
wsgi_app = "karspexet.wsgi"
bind = ":8000"


def on_reload(server):
    raise SystemExit("Received SIGHUP, exiting instead of reloading")
