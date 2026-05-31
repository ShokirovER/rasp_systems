import requests
import time
from cryptography.fernet import Fernet

# загрузка ключа
with open("encryption_key.txt", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# ввод задачи
task = input(
    "Введите задачу: "
)

# шифрование
encrypted = fernet.encrypt(
    task.encode()
).decode()

# отправка
resp = requests.post(
    "http://127.0.0.1:8000/api/task",
    json={
        "data": encrypted
    }
)

response_data = resp.json()

task_id = response_data["task_id"]

print(
    f"\nЗадача поставлена в очередь."
)

print(
    f"ID задачи: {task_id}"
)

print(
    "\nОжидание выполнения..."
)

# автоматическая проверка статуса
while True:

    time.sleep(2)

    resp = requests.get(
        f"http://127.0.0.1:8000/status/{task_id}"
    )

    status = resp.json()["status"]

    print(
        f"Статус: {status}"
    )

    if status == "completed":

        print(
            "\nЗадача успешно выполнена."
        )

        break