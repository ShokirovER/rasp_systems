# Лабораторная работа №2. Исследование HTTP-запросов, разработка REST API и настройка Nginx в качестве обратного прокси (вариант 21)

## Цель работы

Изучить методы отправки и анализа HTTP-запросов с использованием инструментов `telnet` и `curl`. Освоить базовую настройку и анализ работы HTTP-сервера `nginx` в качестве веб-сервера и обратного прокси. Изучить и применить на практике концепции архитектурного стиля REST для создания веб-сервисов (API) на языке Python с использованием фреймворка Flask.

# Теоретические основы
- **HTTP** - протокол прикладного уровня для передачи данных
- **REST API** - архитектурный стиль для создания веб-сервисов
- **Nginx** - веб-сервер и обратный прокси
- **Reverse Proxy** - сервер, который принимает запросы и перенаправляет их другим серверам

# Часть 1. Проверка состояния сайта gazeta.ru и анализ его заголовков.

## Базовый запрос с выводом заголовков

```bash
curl -I http://gazeta.ru
```

**Результат:**
```
HTTP/1.1 301 Moved Permanently
server: nginx
date: Wed, 13 May 2026 12:00:00 GMT
content-Type: text/html
content-Length: 162
Connection: keep-alive
Location: https://gazeta.ru/
```

## Запрос с автоматическим следованием редиректу

```bash
curl -I -L http://gazeta.ru
```

**Результат:**
```
HTTP/2 200
server: nginx
date: Wed, 13 May 2026 12:00:01 GMT
content-type: text/html; charset=utf-8

```

**Анализ:** До редиректа сервер возвращает код 301 с указанием нового адреса (HTTP → HTTPS), а после редиректа возвращает код 200 с реальным содержимым сайта уже по защищённому протоколу HTTPS.

# Часть 2. Разработка API для "Музыкальные треки"

## Создание виртуального окружения и установка Flask

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
```

**Результат установки:**
```
Successfully installed flask-3.1.3
```

## Код REST API (app.py)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# Хранилище треков (в памяти)
tracks = [
    {'id': 1, 'title': 'Bohemian Rhapsody', 'artist': 'Queen', 'album': 'A Night at the Opera'},
    {'id': 2, 'title': 'Imagine', 'artist': 'John Lennon', 'album': 'Imagine'}
]
next_id = 3  # Счетчик для следующего ID


# 1. GET /api/tracks - получить все треки
@app.route('/api/tracks', methods=['GET'])
def get_tracks():
    """Возвращает список всех треков"""
    return jsonify(tracks)

# 2. GET /api/tracks/<id> - получить один трек по ID
@app.route('/api/tracks/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """Возвращает трек с указанным ID"""
    # Ищет трек с нужным ID
    track = next((t for t in tracks if t['id'] == track_id), None)
    
    if track is None:
        return jsonify({'error': 'Track not found'}), 404
    
    return jsonify(track)

# 3. POST /api/tracks - создать новый трек
@app.route('/api/tracks', methods=['POST'])
def create_track():
    """Добавляет новый трек в коллекцию"""
    global next_id
    
    # Проверяем, что пришел JSON
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    
    # Проверяем наличие всех полей
    required_fields = ['title', 'artist', 'album']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Создаем новый трек
    new_track = {
        'id': next_id,
        'title': data['title'],
        'artist': data['artist'],
        'album': data['album']
    }
    
    tracks.append(new_track)
    next_id += 1
    
    # Возвращаем созданный трек и код 201 (Created)
    return jsonify(new_track), 201


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
```

## Запуск Flask сервера

**Команда:**
```bash
python3 app.py
```

**Вывод:**
```
* Serving Flask app 'app.py'
* Debug mode: on
* Running on http://127.0.0.1:5000
```

## Тестирование API

**Тест 1. GET /api/tracks (получить все треки)**
  
```bash
curl -v http://127.0.0.1:5000/api/tracks
```
**Ответ:**
```json
[
  {
    "album": "A Night at the Opera",
    "artist": "Queen",
    "id": 1,
    "title": "Bohemian Rhapsody"
  },
  {
    "album": "Imagine",
    "artist": "John Lennon",
    "id": 2,
    "title": "Imagine"
  }
]
```

**Тест 2. GET /api/tracks/1 (получить конкретный трек)**
  
```bash
curl http://127.0.0.1:5000/api/tracks/1
```
**Ответ:**
```json
{
  "album": "A Night at the Opera",
  "artist": "Queen",
  "id": 1,
  "title": "Bohemian Rhapsody"
}
```

**Тест 3. POST /api/tracks (создать новый трек)**
  
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"title": "Smells Like Teen Spirit", "artist": "Nirvana", "album": "Nevermind"}' \
http://127.0.0.1:5000/api/tracks
```
**Ответ:**
```json
{
  "album": "Nevermind",
  "artist": "Nirvana",
  "id": 3,
  "title": "Smells Like Teen Spirit"
}
```

# Часть 3. Настройка Nginx как обратного прокси

## Установка Nginx

```bash
sudo apt update
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

Проверим, что Nginx работает:

```bash
sudo systemctl status nginx
```

Получаем такой ответ, значит все работает:

```bash
nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2026-05-13 01:01:12 MSK; 1h 9min ago
```

Далее создадим резервную копию оригинального конфига:

```bash
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
```

Отредактируем конфигурационный файл:

```bash
sudo nano /etc/nginx/sites-available/default
```

**Итоговая конфигурация:**
```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /var/www/html;
    index index.html index.htm;

    server_name _;

    # Обработка обычных запросов (не /api/)
    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Проверка конфигурации и перезапуск

```bash
sudo nginx -t
```

**Результат:**
```
nginx: configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

# Тестирование API через Nginx (порт 80)

## Проверка GET все треки

```bash
curl http://localhost/api/tracks
```

**Ответ:**
```
[
  {
    "album": "A Night at the Opera",
    "artist": "Queen",
    "id": 1,
    "title": "Bohemian Rhapsody"
  },
  {
    "album": "Imagine",
    "artist": "John Lennon",
    "id": 2,
    "title": "Imagine"
  }
]
```

## GET один трек по ID

```bash
curl http://localhost/api/tracks/1
```

**Ответ:**
```
{
  "album": "A Night at the Opera",
  "artist": "Queen",
  "id": 1,
  "title": "Bohemian Rhapsody"
}
```

## POST - создать новый трек

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"title": "Back in Black", "artist": "AC/DC", "album": "Back in Black"}' \
http://localhost/api/tracks
```

**Ответ:**
```
{
  "album": "Back in Black",
  "artist": "AC/DC",
  "id": 4,
  "title": "Back in Black"
}
```

# Сравнение прямого доступа и через Nginx

| Параметр | Прямой доступ (порт 5000) | Через Nginx (порт 80) |
|----------|---------------------------|----------------------|
| URL | http://127.0.0.1:5000/api/tracks | http://localhost/api/tracks |
| Server | Werkzeug (Flask) | nginx/1.24.0 |
| Доступность | Только локально | Через стандартный порт HTTP |


# Вывод

В ходе выполнения лабораторной работы были изучены методы анализа HTTP-запросов с использованием утилит telnet и curl на примере сайта gazeta.ru, который возвращает редирект 301 на HTTPS. Разработан REST API для управления музыкальными треками на фреймворке Flask с поддержкой операций GET и POST. Настроен веб-сервер Nginx в качестве обратного прокси, перенаправляющий запросы с порта 80 на порт 5000, где работает Flask-приложение, что подтверждается заголовком Server: nginx и строкой подключения к порту 80 в выводе curl -v. Все задачи варианта №21 выполнены в полном объеме.



