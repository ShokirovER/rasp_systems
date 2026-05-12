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
