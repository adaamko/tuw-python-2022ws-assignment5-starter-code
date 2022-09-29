import networkx as nx
from flask import Flask, jsonify, request
from pynlp5.constants import ALIAS_PATH, CHARACTER_PATH, TEXT_PATH
from pynlp5.knowledge_graph import KnowledgeGraph

kg = None

HOST = "localhost"
PORT = 5005
app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World"


@app.route("/build")
def build():
    global kg
    serialized_path = request.args.get("serialized_path")

    if serialized_path:
        kg = KnowledgeGraph(TEXT_PATH, CHARACTER_PATH, ALIAS_PATH, serialized_path)
    else:
        kg = KnowledgeGraph(TEXT_PATH, CHARACTER_PATH, ALIAS_PATH)

    return "Built"


@app.route("/serialize")
def serialize():
    global kg
    serialized_path = request.args.get("serialized_path")

    if kg:
        serialized_kg = kg.serialize_kg(serialized_path)
        return "Serialized"
    else:
        return "No Knowledge Graph to serialize"


@app.route("/get_characters")
def get_characters():
    global kg
    characters = kg.get_characters()

    return jsonify(characters)


@app.route("/neighbors")
def kg_neighbors():
    global kg
    character = request.args.get("character")
    distance = request.args.get("distance")
    if distance:
        distance = int(distance)
    else:
        distance = 1

    if kg is None:
        return jsonify({"error": "Knowledge graph not loaded."})

    neighbors = kg.get_character_neighbors(character, distance)

    subgraph = nx.cytoscape_data(neighbors)

    print("Returning subgraph...")
    print(neighbors.nodes)

    return jsonify(subgraph)


@app.route("/get_character_with_most_connections")
def get_character_with_most_connections():
    global kg
    character, connections, subgraph = kg.get_character_with_most_connections()

    return jsonify(
        {
            "character": character,
            "connections": connections,
            "subgraph": nx.cytoscape_data(subgraph),
        }
    )


@app.route("/get_isolated_characters")
def get_isolated_characters():
    global kg
    characters, subgraph = kg.get_isolated_characters()

    return jsonify({"characters": characters, "subgraph": nx.cytoscape_data(subgraph)})


@app.route("/shortest_path")
def shortest_path():
    global kg
    character1 = request.args.get("character1")
    character2 = request.args.get("character2")

    sp, sum_of_path = kg.shortest_path_between_characters(
        character1, character2
    )

    subgraph = nx.cytoscape_data(sp)

    print("Returning shortest path")
    print(sp.nodes)

    return jsonify({"shortest_path": subgraph, "sum_of_path_weights": sum_of_path})


if "__main__" == __name__:
    app.run(debug=True, host=HOST, port=PORT)
