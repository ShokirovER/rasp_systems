import time
import redis
from flask import Flask

app = Flask(__name__)

cache = redis.Redis(host='cache', port=6379)

def get_hit_count():
    retries = 5

    while True:
        try:
            return cache.incr('hits')

        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc

            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():

    count = get_hit_count()

    return '''
    <h1 style="color:green">
        Бизнес-стенд "Инновации"
    </h1>

    <p>
        Посетителей сегодня:
        <strong>{}</strong>
    </p>

    <hr>

    <footer>
        ООО Ромашка, 2024
    </footer>
    '''.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
