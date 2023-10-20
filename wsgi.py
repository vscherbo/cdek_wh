#!/usr/bin/env python
""" WSGI entry point

run:
    gunicorn --bind 0.0.0.0:8123 wsgi:app -w 4
    gunicorn --bind 0.0.0.0:8123 wsgi:app -w 2 --threads 3
    gunicorn server:app -k gevent --worker-connections 1000
"""

from cdek_wh_demo import app

if __name__ == "__main__":
    app.run()
