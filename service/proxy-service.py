import requests
from flask import Flask, request, Response
import os
import json
import datetime
import logger as log

app = Flask(__name__)

logger = log.init_logger("dynamic-url-proxy", os.environ.get("LOGLEVEL", "INFO"))

methods = [
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "OPTIONS",
    "HEAD",
    "CONNECT",
    "PATCH",
    "TRACE"
]

GLOBALS = {}
LOCALS = {"datetime": datetime}


def generate_response(response_text, status_code, content_type="application/json"):
    return Response(
        response=response_text,
        status=status_code,
        content_type=content_type)


@app.route("/", methods=methods)
def proxy(path=""):
    url = request.args.get("url")
    if not url:
        return generate_response(
        json.dumps({
        "is_success": False,
        "message": "missing mandatory parameter"
        }),
        400)
    if url[0] == "\"" and url[-1] == "\"":
        url = url[1:-1]
    quote_opener = request.args.get("quote_opener", "[")
    quote_closer = request.args.get("quote_closer", "]")

    params2forward = dict([])
    logger.debug(request.args)
    try:
        for key, value in request.args.items():
            if key == "url":
                continue
            elif url.find(quote_opener + key + quote_closer) >= 0:
                evaluated_value = eval(value, GLOBALS, LOCALS)
                logger.debug("eval('%s') reveals '%s'" % (value,
                                                          evaluated_value))
                url = url.replace(quote_opener + key + quote_closer,
                                  str(evaluated_value))
        r = requests.request(
            method=request.method,
            url=url,
            headers=request.headers,
            auth=request.authorization,
            params=params2forward,
            json=request.get_json(),
            data=request.data)
        return generate_response(r.text,
                                 r.status_code,
                                 r.headers.get("Content-Type"))

    except Exception as e:
        logger.exception(e)
        return generate_response(
            json.dumps({
                "is_success": False,
                "message": str(e)
            }),
            500)


if __name__ == "__main__":
    if os.environ.get("WEBFRAMEWORK", "").lower() == "flask":
        app.run(
            threaded=True,
            debug=True,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)))
    else:
        import cherrypy

        app = log.add_access_logger(app, logger)
        cherrypy.tree.graft(app, "/")

        # Set the configuration of the web server to production mode
        cherrypy.config.update({
            "environment": "production",
            "engine.autoreload_on": False,
            "log.screen": True,
            "server.socket_port": int(os.environ.get("PORT", 5000)),
            "server.socket_host": "0.0.0.0"
        })

        # Start the CherryPy WSGI web server
        cherrypy.engine.start()
        cherrypy.engine.block()
