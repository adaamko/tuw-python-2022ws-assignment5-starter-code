import argparse
import os

import requests
import streamlit as st
from pynlp5.constants import SERIALIZED_PATH

from utils import (convert_networkx_to_agraph, init_session_states,
                   json_to_networkx)

# ===============================================================================
# Functions for querying the backend flask based API
# ===============================================================================

# Note the caching decorator
# This is to cache the results of the function
# so that the function is not called everytime the page is refreshed
@st.cache
def build_kg(serialized_path=None):
    if serialized_path:
        response = requests.get(
            f"http://localhost:5005/build?serialized_path={serialized_path}"
        )
    else:
        response = requests.get("http://localhost:5005/build")


@st.cache
def get_characters():
    response = requests.get("http://localhost:5005/get_characters")
    return response.json()


def serialize_kg(serialized_path):
    response = requests.get(
        f"http://localhost:5005/serialize?serialized_path={serialized_path}"
    )


@st.cache
def query_neighbor(character):
    response = requests.get(f"http://localhost:5005/neighbors?character={character}")
    return response.json()


@st.cache
def query_neighbor_with_distance(character, distance):
    response = requests.get(
        f"http://localhost:5005/neighbors?character={character}&distance={distance}"
    )
    return response.json()


# @st.cache
def get_characters_with_most_connections():
    response = requests.get("http://localhost:5005/get_character_with_most_connections")
    d = response.json()
    character = d["character"]
    connections = d["connections"]
    graph = d["subgraph"]

    return character, connections, graph


# @st.cache
def get_isolated_characters():
    response = requests.get("http://localhost:5005/get_isolated_characters")
    d = response.json()
    characters = d["characters"]
    graph = d["subgraph"]

    return characters, graph


# @st.cache
def shortest_path(character1, character2):
    response = requests.get(
        f"http://localhost:5005/shortest_path?character1={character1}&character2={character2}"
    )
    return response.json()


# ==============================================================================
# This is the main function where we will build our Streamlit app
# ==============================================================================
def main(args):
    # First we setup the page layout
    st.set_page_config(layout="wide")
    # We create the title of our app
    st.markdown(
        "<h1 style='text-align: center; color: black;'>Knowledge graph</h1>"
        "<h2 style='text-align: center; color: black;'>using streamlit for data science tasks</h2>",
        unsafe_allow_html=True,
    )
    # Initialize the session states
    init_session_states()

    knowledge_graph_path = args.knowledge_graph

    # We build the knowledge graph
    with st.expander("Build Knowledge Graph", expanded=True):
        if st.button("Build"):
            # Check if serialized path file exists in the system
            if knowledge_graph_path and os.path.isfile(knowledge_graph_path):
                st.write("Serialized Knowledge Graph already exists.")
                build_kg(knowledge_graph_path)
            else:
                build_kg()
            st.session_state.built = True

        # If we didn't provide a knowledge graph path
        # We can serialize the knowledge graph
        if not knowledge_graph_path:
            serialize_path = st.text_input(
                "Enter a path to serialize the knowledge graph to",
                value=SERIALIZED_PATH,
            )
            if st.button("Serialize"):
                serialize_kg(serialize_path)
                st.session_state.serialized = True

    # This is important for the page layout
    # We will work with 2 columns
    # The first column will let you choose characters and algorithms
    # The second will be for displaying the results
    col1, col2 = st.columns(2)

    # We only want to display the rest of the app if the knowledge graph is built
    # Note the use of session states
    if st.session_state.built:
        with col1:
            # We create a selectbox to choose the character
            if not st.session_state.characters:
                st.session_state.characters = get_characters()

            # We create a selectbox to choose which algorithm to use
            query_type = st.selectbox(
                "Query Type",
                [
                    "Neighbors",
                    "Neighbors with distance",
                    "Character with most connections",
                    "Isolated Characters",
                    "Shortest Path",
                ],
            )

            # Based on our choice of algorithm we will display different widgets
            # We will save the values of these widgets in session states
            # So that we can use them later
            # We save the queried graph and other information in session states
            if query_type == "Neighbors":
                character = st.selectbox(
                    "Select a character", st.session_state.characters
                )

                if st.button("Get Neighbors"):
                    neighbors = query_neighbor(character)
                    st.session_state.current_graph = json_to_networkx(neighbors)

            elif query_type == "Neighbors with distance":
                character = st.selectbox(
                    "Select a character", st.session_state.characters
                )
                distance = st.number_input("Enter distance", value=1)

                if st.button("Get Neighbors"):
                    neighbors = query_neighbor_with_distance(character, distance)
                    st.session_state.current_graph = json_to_networkx(neighbors)

            elif query_type == "Character with most connections":
                if st.button("Get Character"):
                    (
                        character,
                        connections,
                        graph,
                    ) = get_characters_with_most_connections()
                    st.session_state.info = f"Character with most connections is {character} with {connections} connections."
                    st.session_state.current_graph = json_to_networkx(graph)

            # ==============================================================================
            # TASK 1: Add a query type to get the isolated characters
            # ==============================================================================
            elif query_type == "Isolated Characters":
                if st.button("Get Characters"):
                    st.error("Not implemented yet")
                    # UNCOMMENT THE FOLLOWING LINES FOR TASK 1
                    
                    # characters, graph = get_isolated_characters()
                    # st.session_state.info = (
                    #     f"Isolated characters are {', '.join(characters)}."
                    # )
                    # st.session_state.current_graph = json_to_networkx(graph)

            # ==============================================================================
            # TASK 2: Add a query type to get the shortest path between two characters
            # ==============================================================================
            elif query_type == "Shortest Path":
                st.error("Not implemented yet")
                # UNCOMMENT THE FOLLOWING LINES FOR TASK 2

                # character1 = st.selectbox(
                #     "Select a character", st.session_state.characters
                # )
                # character2 = st.selectbox(
                #     "Select a character", st.session_state.characters, index=1
                # )

                # if st.button("Get Shortest Path"):
                #     d = shortest_path(character1, character2)
                #     path = d["shortest_path"]
                #     st.session_state.current_graph = json_to_networkx(path)

                #     num_edges = len(st.session_state.current_graph.edges())
                #     sum_of_path_weights = d["sum_of_path_weights"]
                #     st.session_state.info = f"Shortest path between {character1} and {character2} has {num_edges} number of edges with a sum weights of {sum_of_path_weights}"

        with col2:
            # We display the saved informatin and the built graph here using the agraph package in streamlit
            if st.session_state.info:
                st.write("Info")
                st.write(st.session_state.info)
            if st.session_state.current_graph:
                agraph = convert_networkx_to_agraph(st.session_state.current_graph)


def get_args():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-kg",
        "--knowledge-graph",
        default=None,
        type=str,
        help="Path to knowledge graph",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    main(args)
