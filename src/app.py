import json_logging, logging, sys, flask
from flask import jsonify, request
from faker import Faker
fake = Faker()

# Flask
app = flask.Flask(__name__)

# logging configuration
json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

request_logger = json_logging.get_request_logger()
handler = logging.handlers.RotatingFileHandler(filename='log_req.log', maxBytes=5000000, backupCount=10)
handler.setFormatter(json_logging.JSONRequestLogFormatter())
request_logger.addHandler(handler)


@app.route('/')
def home():
    return jsonify({'Hello': 'World'})


@app.route('/students')
def students():
    no_students = request.args.get("no_students")
    if (no_students == None):
        return jsonify({'crazy': True})

    no_students = int(no_students)
    students = []
    for _ in range(no_students):
        students.append({'name': fake.name(), 'address': fake.address()})

    return jsonify(students)

@app.route('/movies')
def movies():
    movies = [
        'Inception',
        'Interstellar',
        'black hawk down',
        'cinderella man',
        'a beautiful mind'
    ]

    return jsonify(movies)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(5000))