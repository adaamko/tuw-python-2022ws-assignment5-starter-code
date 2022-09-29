from pynlp5.knowledge_graph import KnowledgeGraph
import os

dir_name = os.path.dirname(os.path.realpath(__file__))
CHARACTER_PATH = os.path.join(dir_name, "characters_test.txt")
ALIAS_PATH = os.path.join(dir_name, "character_aliases_test.json")
TEXT_PATH = os.path.join(dir_name, "test_lines.txt")

kg = KnowledgeGraph(TEXT_PATH, CHARACTER_PATH, ALIAS_PATH)


def test_kg():
    assert len(kg.get_characters()) == 19
    assert "Sansa Stark" in kg.get_characters()


def test_query_neighbor():
    neighbors = kg.get_character_neighbors("Sansa Stark")
    assert len(neighbors) == 5
    assert "Joffrey Baratheon" in neighbors.nodes()


def test_query_neighbor_with_distance():
    neighbors = kg.get_character_neighbors("Sansa Stark", depth=2)
    assert len(neighbors) == 7
    assert "Mycah" in neighbors.nodes()


def test_character_with_most_connections():
    character, connections, subgraph = kg.get_character_with_most_connections()
    assert character == "Sansa Stark"
    assert connections == 10
    assert len(subgraph.nodes) == 5


def test_isolated_characters():
    characters, subgraph = kg.get_isolated_characters()
    assert len(characters) == 6


def test_shortest_path():
    shortest_path, sum_of_path = kg.shortest_path_between_characters(
        "Sansa Stark", "Mycah"
    )
    assert len(shortest_path) == 3
    assert sum_of_path == 7


if __name__ == "__main__":
    test_kg()
