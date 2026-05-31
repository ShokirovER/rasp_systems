from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

servers = [
    "https://localhost:5001",
    "https://localhost:5002"
]


@app.route("/api/task", methods=["POST"])
def create_task():

    for server in servers:

        try:

            resp = requests.post(
                server + "/api/task",
                json=request.json,
                cert=(
                    "client_cert.pem",
                    "client_key.pem"
                ),
                verify=False
            )

            return jsonify(resp.json())

        except Exception:

            print(
                "Server failed:",
                server
            )

    return jsonify({
        "error": "all servers down"
    }), 500


@app.route("/status/<task_id>", methods=["GET"])
def status(task_id):

    for server in servers:

        try:

            resp = requests.get(
                server + f"/status/{task_id}",
                cert=(
                    "client_cert.pem",
                    "client_key.pem"
                ),
                verify=False
            )

            return jsonify(resp.json())

        except Exception:

            continue

    return jsonify({
        "error": "all servers down"
    }), 500


if __name__ == "__main__":
    app.run(port=8000)