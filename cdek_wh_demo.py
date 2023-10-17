#!/usr/bin/env python
""" CDEK webhooks listener
gunicorn -w 2 -b 0.0.0.0:3000 myapp:app
"""

from flask import Flask, request, Response

app = Flask(__name__)
@app.route('/', methods=['POST'])
def return_response():
    """ POST handler
    """
    if request.method == 'POST':
        print(request.json)
        ## Do something with the request.json data.
    return Response(status=200)

if __name__ == "__main__":
    app.run(host='192.168.1.101', debug=True, port=8123)
