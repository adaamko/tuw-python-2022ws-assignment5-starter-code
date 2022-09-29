from flask import Flask, request, jsonify

HOST = "localhost"
PORT = 5004
app = Flask(__name__)

my_dictionary = {"a": 1, "b": 2, "c": 3}


@app.route("/", methods=["GET"])
def index():
    return "Hello World"


@app.route("/hello", methods=["GET"])
def hello():
    name = request.args.get("name")
    return f"Hello {name}"


@app.route("/add_data", methods=["POST"])
def add_data():
    data = request.get_json()
    my_dictionary[data["key"]] = data["value"]

    return "Added"


@app.route("/get_data", methods=["GET"])
def get_data():
    return my_dictionary


if "__main__" == __name__:
    app.run(debug=True, host=HOST, port=PORT)
