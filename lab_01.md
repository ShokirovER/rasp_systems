# Вариант 21 

Реализовать gRPC-сервис OrderManager с методом:

GetOrderStatus(OrderRequest)

Метод должен возвращать статус заказа и дату доставки по его идентификатору.
Тип взаимодействия — Unary RPC (один запрос → один ответ).

# 🏗 Архитектура решения

В работе реализована классическая клиент-серверная архитектура.
```
+-------------+        gRPC         +-------------+
|   Клиент    |  <--------------->  |   Сервер    |
|  client.py  |                     |  server.py  |
+-------------+                     +-------------+
                                          |
                                          |
                                   +---------------+
                                   | Логика заказа |
                                   |  (в памяти)   |
                                   +---------------+
```
# Компоненты системы

Client (client.py)
Отправляет запрос серверу с ID заказа и получает информацию о его статусе.

Server (server.py)
Обрабатывает запрос клиента, проверяет ID и возвращает данные.

order.proto
Контракт взаимодействия. Описывает метод сервиса и структуры сообщений.

# 🧩 Описание реализации

В рамках лабораторной работы был создан gRPC-сервис OrderManager.

Описание сервиса выполнено в файле
```
order.proto

```
Метод GetOrderStatus реализован как Unary RPC, что означает: клиент отправляет один запрос, сервер возвращает один ответ.

📷 Содержимое файла product.proto

```protobuf
syntax = "proto3";

package order;

// Сервис для управления заказами
service OrderManager {
  // Unary RPC: метод получения статуса заказа по его ID
  rpc GetOrderStatus (OrderRequest) returns (OrderResponse) {}
}

// Сообщение-запрос: содержит идентификатор заказа
message OrderRequest {
  string order_id = 1;
}

// Сообщение-ответ: содержит информацию о текущем состоянии заказа
message OrderResponse {
  string status = 1;        // Статус заказа (например, "Доставлен")
  string delivery_date = 2; // Ожидаемая дата доставки
}
```
⚙ Генерация gRPC-кода

После создания order.proto была выполнена команда:
```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. order.proto
```
В результате автоматически были созданы файлы:
```
order_pb2.py
```
```
order_pb2_grpc.py
```
🖥 Реализация сервера

Серверная часть реализована в файле server.py. Создан класс OrderManagerServicer, наследующийся от OrderManagerServicer. В методе GetOrderStatus выполняется поиск заказа по ID.

``` python
import grpc
from concurrent import futures
import order_pb2
import order_pb2_grpc

class OrderManagerServicer(order_pb2_grpc.OrderManagerServicer):
    def GetOrderStatus(self, request, context):
        print(f"Получен запрос для заказа ID: {request.order_id}")
        # Логика имитации поиска
        if request.order_id == "123":
            status = "Доставлен"
            date = "2026-04-24"
        else:
            status = "Не найден"
            date = "N/A"
        return order_pb2.OrderResponse(status=status, delivery_date=date)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderManagerServicer_to_server(OrderManagerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Сервер запущен на порту 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```
💻 Реализация клиента
Клиентская часть реализована в файле client.py. Подключение выполняется через grpc.insecure_channel('localhost:50051').

``` python
import grpc
import order_pb2
import order_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = order_pb2_grpc.OrderManagerStub(channel)
        print("Запрашиваю статус заказа №123...")
        request = order_pb2.OrderRequest(order_id="123")
        try:
            response = stub.GetOrderStatus(request)
            print(f"Ответ сервера: Статус — {response.status}, Дата — {response.delivery_date}")
        except grpc.RpcError as e:
            print(f"Ошибка при вызове: {e.details()}")

if __name__ == '__main__':
    run()
```
🧠 Используемые технологии

Python 3

gRPC

Protocol Buffers

Virtual Environment (venv)

🚀 Запуск проекта

Активация окружения
```
.\venv\Scripts\activate
```

Запуск сервера
```
python server.py
```

Запуск клиента
```
python client.py
```

📊 Результат работы

Работа сервера
```
(venv) PS C:\Users\egors\Desktop\grpc_order_lab> .\venv\Scripts\activate
(venv) PS C:\Users\egors\Desktop\grpc_order_lab> python server.py
Сервер запущен на порту 50051...
```

Работа клиента
```
(venv) PS C:\Users\egors\Desktop\grpc_order_lab> python client.py
Запрашиваю статус заказа №123...
Ответ сервера: Статус — Доставлен, Дата — 2026-04-24
```

Сервис корректно принимает ID заказа, обрабатывает его и возвращает статус с датой. Ошибки при передаче данных отсутствуют.

🧾 Вывод

В ходе выполнения лабораторной работы я реализовал клиент-серверный сервис OrderManager с использованием технологии gRPC. Был спроектирован контракт (IDL) в .proto файле, сгенерирован программный код для Python и реализована бизнес-логика обработки запросов. Тестирование показало стабильную работу Unary RPC взаимодействия: клиент успешно получает данные по ID заказа от сервера.
