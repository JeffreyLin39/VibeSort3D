# rest_server.py
import base64
import logging

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/ping", methods=["POST"])
def ping():
    data = request.get_json(force=True, silent=False)
    if "payload" not in data:
        return jsonify({"error": "missing payload"}), 400
    # Echo the payload back verbatim
    return jsonify({"payload": data["payload"]})


if __name__ == "__main__":
    # Flask’s builtin server is enough for a controlled benchmark
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.info("REST server listening on :8080")
    app.run(host="0.0.0.0", port=8080, threaded=True)
