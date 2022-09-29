import json
import re
from collections import defaultdict
from typing import Iterable, Tuple

import networkx as nx
from more_itertools import pairwise
from tqdm import tqdm


class KnowledgeGraph:
    def __init__(
        self,
        text_path: str,
        characters_path: str,
        character_aliases_path: str,
        serialized_kg: str = None,
    ) -> None:
        """This is the graph class that will contain the knowledge graph and implement all the preprocessing and graph building methods.
        For the preprocessing, we will use the characters and character aliases files.
        The characters file contains a list of all the characters in the text.
        The character aliases file contains a list of all the aliases of the characters.
        For graph algorithms we will use the networkx library, this will be the backbone of the graph class.

        Args:
            text_path (str): The path to the text file, it contains the text line by line.
            characters_path (str): The path to the characters file, it contains the characters line by line.
            character_aliases_path (str): The path to the character aliases file, it contains the character aliases as a json object.
            serialized_kg (str, optional): The path to the serialized knowledge graph, if present we won't build it. Defaults to None.
        """

        # The knowledge graph, empty at first.
        self.kg = nx.Graph()

        # The characters list, empty at first.
        self.characters = []
        # We read the characters from the file.
        self.read_characters(characters_path)

        # We will also use only the first names of the characters, so we build a dictionary of first names.
        # The keys are the first names and the values are the number of times the first name appears in the characters list.
        # This is because if multiple characters have the same first name, we will not use it as a first name because we don't know which character it refers to.
        # This would be an interesting Natural Language Processing problem to solve, We have a class for that :).
        self.character_first_names = defaultdict(int)
        self.build_first_names()

        # The character aliases dictionary, empty at first.
        self.character_aliases = {}
        # We read the character aliases from the file.
        # The character aliases are a json object, so we use the json library to read it.
        # We do this to recognize more mentions of the characters.
        self.read_character_aliases(character_aliases_path)

        # We will use regular expressions to recognize mentions of the characters.
        # We compile the regular expressions for the characters, the first names and the aliases.
        # We do this to speed up the recognition of mentions of the characters. (Only need to compile the regex once)
        self.characters_regex = {}
        self.character_first_names_regex = {}
        self.character_aliases_regex = {}
        self.compile_characters_regex()

        # If the serialized knowledge graph is present, we deserialize it.
        # Else we build the knowledge graph.
        if serialized_kg:
            self.deserialize_kg(serialized_kg)
        else:
            self.build_kg(text_path)

    def serialize_kg(self, filename: str) -> None:
        """We use networkx to serialize the knowledge graph to a json file.

        Args:
            filename (str): Path to the file where we will serialize the knowledge graph.
        """
        json_graph = nx.cytoscape_data(self.kg)
        with open(filename, "w") as f:
            json.dump(json_graph, f)

    def deserialize_kg(self, filename: str) -> None:
        """
        Deserialize the knowledge graph from a file.

        Args:
            filename (str): Path to the file where the knowledge graph is serialized.
        """
        with open(filename, "r") as f:
            json_graph = json.load(f)
            self.kg = nx.cytoscape_graph(json_graph)

    # ================================================================================================
    # Preprocessing and regex methods
    # ================================================================================================

    def build_first_names(self) -> None:
        """
        Build the dictionary of first names and mentions.
        """
        for character in self.characters:
            first_name = character.split(" ")[0]
            self.character_first_names[first_name] += 1

    def read_character_aliases(self, filename: str) -> None:
        """Read the character aliases from the file.

        Args:
            filename (str): Path to the file where the character aliases are.
        """
        with open(filename, "r") as f:
            self.character_aliases = json.load(f)

    def read_characters(self, filename: str) -> None:
        """_summary_

        Args:
            filename (str): _description_
        """
        with open(filename, "r") as f:
            for line in f:
                self.characters.append(line.strip())

    def compile_characters_regex(self) -> None:
        """
        Compile the regular expressions for the characters, the first names and the aliases.
        """

        # For each character we compile a regular expression that matches the character name.
        # We build a dictionary where the keys are the characters and the values are the compiled regular expressions.
        for character in self.characters:
            self.characters_regex[character] = re.compile(r"\b" + character + r"\b")

        # For each first name we compile a regular expression that matches the first name.
        for first_name in self.character_first_names:
            self.character_first_names_regex[first_name] = re.compile(
                r"\b" + first_name + r"\b"
            )

        # For each alias we compile a regular expression that matches the alias.
        # This is a little more complicated, because we want to match all the aliases.
        # For this we build a big regular expression that matches all the aliases.
        for character in self.character_aliases:
            character_aliases_regex = ""
            for alias in self.character_aliases[character]:
                if alias not in self.characters:
                    character_aliases_regex += r"\b" + alias + r"\b|"
            if character_aliases_regex != "":
                self.character_aliases_regex[character] = re.compile(
                    character_aliases_regex.strip("|")
                )

    def match_character(self, text: str, character: str) -> bool:
        """Match a character in a text.

        Args:
            text (str): The text where we will search for the character.
            character (str): The character we will search for.

        Returns:
            bool: True if the character is present in the text, False otherwise.
        """
        # Getting the compiled regular expression for the character.
        first_name = character.split(" ")[0]
        character_regex = self.characters_regex[character]
        character_first_name_regex = self.character_first_names_regex[first_name]

        # If the character has aliases, we get the compiled regular expression for the aliases.
        if character in self.character_aliases_regex:
            character_aliases_regex = self.character_aliases_regex[character]
        else:
            character_aliases_regex = None

        # We search for the character in the text.
        if character_regex.search(text):
            return True
        # If the character has aliases, we search for the aliases in the text.
        elif character_aliases_regex and character_aliases_regex.search(text):
            return True
        else:
            # If the character has a first name, we search for the first name in the text
            # But only if the first name is not a first name of another character.
            # And if the first name is not in a list of common first names.
            if self.character_first_names[
                first_name
            ] == 1 and first_name.lower() not in ["the", "a", "an", "lady"]:
                if character_first_name_regex.search(text):
                    return True
            else:
                return False

    def build_kg(self, text_path: str) -> None:
        """Build knowledge graph from text file.
        Iterate on the lines of the text path and if the line contains multiple characters
        Add an edge between every characters.
        The nodes will be the characters, the weights of the edges will be how many times the characters are mentioned in the text.

        Args:
            text_path (str): Path to the text file.
        """
        with open(text_path, "r") as f:
            for line in tqdm(f):
                line = line.strip()
                if line == "":
                    continue
                else:
                    character_matches = []
                    # We iterate on the characters and check if the line contains the character.
                    for character in self.characters:
                        # If the line contains the character, we add the character to the list of character matches.
                        if self.match_character(line, character):
                            character_matches.append(character)

                    # If the line contains more than one character, we add an edge between every character.
                    # For this we use the pairwise function from itertools which generates all the possible pairs of characters.
                    # This is important if we have more than two characters in the line.
                    if len(character_matches) > 1:
                        for character1, character2 in pairwise(character_matches):
                            self.kg.add_edge(character1, character2)

                            # If the edge already exists, we increase the weight of the edge.
                            self.kg[character1][character2]["weight"] = (
                                self.kg[character1][character2].get("weight", 0) + 1
                            )
                    # If the line contains only one character, we add the character to the list of isolated nodes.
                    elif len(character_matches) == 1:
                        self.kg.add_node(character_matches[0])
                    else:
                        continue

        return

    # ================================================================================================
    # Graph Algorithms
    # ================================================================================================

    def get_characters(self) -> Iterable[str]:
        """Return matching characters.

        Returns:
            list: List of characters.
        """
        return list(self.kg.nodes())

    def get_character_neighbors(self, character: str, depth: int = 1) -> nx.Graph:
        # generate docstring
        """Return the neighbors of a character.
        We apply a BFS to get the neighbors of the character.

        Args:
            character (str): Character to get neighbors for.
            depth (int, optional): Depth of the neighbors. Defaults to 1.

        Returns:
            nx.Graph: The neighbors of the character.
        """

        # We only need the edges between the character and its neighbors.
        # For this we apply bfs_edges to get the edges of the subgraph, this breadth first search will start from the character.
        # Important to note that we didn't use depth first search because then it might be possible that we don't get the neighbors of the character.
        edges = list(nx.bfs_edges(self.kg, source=character, depth_limit=depth))
        subgraph = self.kg.edge_subgraph(edges)

        return subgraph

    def get_character_with_most_connections(self) -> Tuple[str, int, nx.Graph]:
        """Get the character that is most connected to other characters.

        Returns:
            Tuple[str, int, nx.Graph]: The character with the most connections, the number of connections and the subgraph of the character.
        """

        # First we get the degree (number of connections) of each node (character) in the graph.
        # Then we sort the nodes by their degree and get the node with the highest degree.
        character, connections = max(
            self.kg.degree(weight="weight"), key=lambda x: x[1]
        )

        # We get the subgraph of the character with the most connections.
        # But we only need the edges between the character and its neighbors.
        # For this we apply dfs_edges to get the edges of the subgraph, this depth first search will start from the character.
        edges = list(nx.dfs_edges(self.kg, source=character, depth_limit=1))
        # Then we only keep the edges that are between the character and its neighbors.
        subgraph = self.kg.edge_subgraph(edges)

        return character, connections, subgraph

    # ================================================================================================
    # TASK 1
    # ================================================================================================
    def get_isolated_characters(self) -> Tuple[Iterable[str], nx.Graph]:
        """Get the characters that are not connected to other characters.

        Returns:
            Tuple[Iterable[str], nx.Graph]: The characters that are not connected to other characters and the subgraph of the characters.
        """
        # TODO: Implement this function.

        return None, None

    # ================================================================================================
    # TASK 2
    # ================================================================================================
    def shortest_path_between_characters(
        self, character1: str, character2: str
    ) -> Tuple[nx.Graph, int]:
        # generate docstring
        """Get the shortest path between two characters.

        Args:
            character1 (str): First character.
            character2 (str): Second character.

        Returns:
            Tuple[nx.Graph, int]: The shortest path between the characters and the length of the path with the weights of the edges.
        """

        # TODO: Implement this function.

        return None, None
