#!/usr/bin/env python
""" CDEK webhooks listener
"""

from flask import Flask, request, Response

APP = Flask(__name__)
@APP.route('/', methods=['POST'])
def return_response():
    """ POST handler
    """
    if request.method == 'POST':
        print(request.json)
        ## Do something with the request.json data.
    return Response(status=200)

if __name__ == "__main__":
    APP.run(host='192.168.1.101', debug=True, port=8123)
