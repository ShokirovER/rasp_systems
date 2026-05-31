from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import ssl
import sys
import threading
import time

app = Flask(__name__)

# загрузка ключа Fernet
with open("encryption_key.txt", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# хранилище задач
tasks = {}

# счетчик задач
task_counter = 0


def process_task(task_id):
    """
    Имитация долгой обработки задачи
    """

    print(f"Начата обработка задачи {task_id}")

    time.sleep(10)

    tasks[task_id]["status"] = "completed"

    print(f"Задача {task_id} завершена")


@app.route("/api/task", methods=["POST"])
def create_task():

    global task_counter

    encrypted = request.json["data"]

    try:

        decrypted = fernet.decrypt(
            encrypted.encode()
        ).decode()

        task_counter += 1

        task_id = str(task_counter)

        tasks[task_id] = {
            "task": decrypted,
            "status": "processing"
        }

        thread = threading.Thread(
            target=process_task,
            args=(task_id,)
        )

        thread.start()

        return jsonify({
            "task_id": task_id
        })

    except Exception:

        return jsonify({
            "error": "decryption failed"
        }), 400


@app.route("/status/<task_id>", methods=["GET"])
def get_status(task_id):

    if task_id not in tasks:

        return jsonify({
            "error": "task not found"
        }), 404

    return jsonify({
        "task_id": task_id,
        "status": tasks[task_id]["status"]
    })


if __name__ == "__main__":

    port = int(sys.argv[1])

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER
    )

    context.load_cert_chain(
        "server_cert.pem",
        "server_key.pem"
    )

    context.load_verify_locations(
        "ca_cert.pem"
    )

    context.verify_mode = ssl.CERT_REQUIRED

    app.run(
        host="0.0.0.0",
        port=port,
        ssl_context=context
    )