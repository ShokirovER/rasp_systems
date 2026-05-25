# Лабораторная работа 3.1. Организация асинхронного взаимодействия микросервисов с помощью брокера сообщений

## Вариант 21

## 📌 Цель работы

Изучить и реализовать два ключевых подхода к взаимодействию между сервисами:

- Синхронное прямое взаимодействие с использованием gRPC.
- Асинхронное взаимодействие через брокер сообщений RabbitMQ.
- Освоить развертывание инфраструктурных компонентов с помощью Docker.

---

## 📁 Структура проекта

lab_3/
├── grpc_sync/

│ ├── message_service.proto # Контракт gRPC с 3 методами

│ ├── message_service_pb2.py # Сгенерированный код protobuf

│ ├── message_service_pb2_grpc.py # Сгенерированный код gRPC

│ ├── grpc_server.py # Реализация gRPC сервера

│ └── grpc_client.py # Тестовый клиент gRPC

│
└── rabbitmq_async/

├── docker-compose.yml # Конфигурация RabbitMQ

├── producer.py # Отправляет задачи в очередь

└── consumer.py # Читает очередь, вызывает gRPC


---

## 📌 Часть 1. Синхронное взаимодействие (gRPC)


**Схема:**
```
   📤 Producer  ----> 🐰 RabbitMQ  ----> 📥 Consumer  ---->  ⚡gRPC Сервер
   
     (отправляет)        (очередь)          (забирает)         (обрабатывает)
```


### Описание

Клиент вызывает gRPC сервер и синхронно ожидает ответа. Сервер выполняет бизнес-логику и возвращает результат. Взаимодействие происходит напрямую, без посредников.

### Методы gRPC сервера

| Метод | Описание | Вход | Выход |

|-------|----------|------|-------|

| `CacheSet` | Сохраняет пару ключ-значение в кэш | `key`, `value` | `status: OK` |

| `Base64Process` | Кодирует или декодирует строку в base64 | `action` (encode/decode), `data` | `result` |

| `CountCharsNoSpaces` | Подсчитывает количество символов без пробелов | `text` | `count` |

---

## 📌 Часть 2. Асинхронное взаимодействие (RabbitMQ + gRPC)

### Схема работы

**Схема:**
```
   📤 Producer  ----> 🐰 RabbitMQ  ----> 📥 Consumer  ---->  ⚡gRPC Сервер
   
     (отправляет)        (очередь)          (забирает)         (обрабатывает)
```


### Описание компонентов

| Компонент | Назначение |

|-----------|------------|

| **Producer** | Отправляет задачи в очередь RabbitMQ |

| **RabbitMQ** | Брокер сообщений. Хранит очередь `task_queue`. Веб-интерфейс на порту `15672` |

| **Consumer** | Забирает задачи из очереди, парсит префикс и вызывает соответствующий метод gRPC сервера |

| **gRPC Сервер** | Выполняет бизнес-логику на порту `50051`, возвращает результат |


### Форматы сообщений Producer

| Префикс | Пример | Что делает gRPC |

|---------|--------|-----------------|

| `cache:` | `cache:user:Alice` | Сохраняет в кэш `user=Alice` |

| `encode:` | `encode:Hello` | Кодирует `Hello` в base64 |

| `decode:` | `decode:SGVsbG8=` | Декодирует из base64 |

| `count:` | `count:Hello World` | Считает символы без пробелов (результат: 10) |


### Преимущества асинхронного подхода

- Producer не ждёт обработки сообщения
- Сообщения накапливаются в очереди при отключенном Consumer
- Можно запустить несколько Consumer'ов для параллельной обработки
- Система остаётся работоспособной при временных сбоях компонентов

---

## 🐳 Развертывание RabbitMQ через Docker

### Файл `docker-compose.yml`

```yaml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3.9-management
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=user
      - RABBITMQ_DEFAULT_PASS=password

**Запуск RabbitMQ**

``` bash
cd ~/Desktop/lab_3/rabbitmq_async
docker compose up -d
```

**Проверка статуса контейнера**

``` bash
docker ps
```
ТУТ СКРИНШОТ С САЙТА

```
http://localhost:15672
 логин: user,
 пароль: password
```

## Реализация сервисов

**message_service.proto**

```protobuf
syntax = "proto3";

package message;

service MessageService {
    rpc CacheSet (CacheRequest) returns (CacheResponse) {}
    rpc Base64Process (Base64Request) returns (Base64Response) {}
    rpc CountCharsNoSpaces (TextRequest) returns (CountResponse) {}
}

message CacheRequest {
    string key = 1;
    string value = 2;
}

message CacheResponse {
    string status = 1;
}

message Base64Request {
    string action = 1;
    string data = 2;
}

message Base64Response {
    string result = 1;
}

message TextRequest {
    string text = 1;
}

message CountResponse {
    int32 count = 1;
}
```

**Генерация gRPS кода**

```bash
cd ~/Desktop/lab_3/grpc_sync
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. message_service.proto
```

**grps_server.py**

```python
import grpc
from concurrent import futures
import base64
import message_service_pb2
import message_service_pb2_grpc

cache = {}

class MessageServiceServicer(message_service_pb2_grpc.MessageServiceServicer):
    
    def CacheSet(self, request, context):
        cache[request.key] = request.value
        print(f"[КЭШ] {request.key} = {request.value}")
        return message_service_pb2.CacheResponse(status="OK")
    
    def Base64Process(self, request, context):
        if request.action == "encode":
            result = base64.b64encode(request.data.encode()).decode()
            print(f"[BASE64] Закодировано: {request.data} -> {result}")
        elif request.action == "decode":
            result = base64.b64decode(request.data).decode()
            print(f"[BASE64] Декодировано: {request.data} -> {result}")
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return message_service_pb2.Base64Response(result="")
        return message_service_pb2.Base64Response(result=result)
    
    def CountCharsNoSpaces(self, request, context):
        count = len(request.text.replace(" ", ""))
        print(f"[ПОДСЧЁТ] '{request.text}' -> {count} символов")
        return message_service_pb2.CountResponse(count=count)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC сервер запущен на порту 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```


**producer.py**

```python
import pika
import sys

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "test:hello"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(delivery_mode=2)
)

print(f" [x] Отправлено: {message}")
connection.close()
```

**consumer.py**

```python
import pika
import grpc
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../grpc_sync'))

import message_service_pb2
import message_service_pb2_grpc

def process_message(message):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = message_service_pb2_grpc.MessageServiceStub(channel)
        
        if message.startswith("cache:"):
            parts = message.split(":")
            if len(parts) >= 3:
                resp = stub.CacheSet(message_service_pb2.CacheRequest(key=parts[1], value=parts[2]))
                return f"CacheSet: {resp.status}"
        
        elif message.startswith("encode:"):
            data = message[7:]
            resp = stub.Base64Process(message_service_pb2.Base64Request(action="encode", data=data))
            return f"Base64 Encode: {resp.result}"
        
        elif message.startswith("decode:"):
            data = message[7:]
            resp = stub.Base64Process(message_service_pb2.Base64Request(action="decode", data=data))
            return f"Base64 Decode: {resp.result}"
        
        elif message.startswith("count:"):
            data = message[6:]
            resp = stub.CountCharsNoSpaces(message_service_pb2.TextRequest(text=data))
            return f"Count (без пробелов): {resp.count}"
        
        return f"Неизвестный формат: {message}"

def callback(ch, method, properties, body):
    message = body.decode()
    print(f" [x] Получено: {message}")
    result = process_message(message)
    print(f" [✓] Результат: {result}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

print(' [*] Ожидание сообщений. Для выхода нажмите CTRL+C')
channel.start_consuming()
```

## Запуск системы

**Терминал 1 — gRPC сервер**

```bash
cd ~/Desktop/lab_3/grpc_sync
python3 grpc_server.py
```

**Терминал 2 — Consumer**

```bash
cd ~/Desktop/lab_3/rabbitmq_async
python3 consumer.py
```

**Терминал 3 — Producer (отправка задач)**

```bash
cd ~/Desktop/lab_3/rabbitmq_async
python3 producer.py <сообщение>
```

## Задание 1. Кэширование данных

Producer отправляет ключ и значение. gRPC сервис сохраняет их в кэш (словарь в памяти) и возвращает OK.

**Отправка сообщений:**

```bash
python3 producer.py cache:user:Alice
python3 producer.py cache:user:Bob
python3 producer.py cache:session:12345
```

**Результат в Consumer:**

```
 [x] Получено: cache:user:Alice
 [✓] Результат: CacheSet: OK
 [x] Получено: cache:user:Bob
 [✓] Результат: CacheSet: OK
 [x] Получено: cache:session:12345
 [✓] Результат: CacheSet: OK

```


