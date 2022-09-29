from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
import networkx as nx


class UpdatedConfig(Config):
    def __init__(self, height: str = "700px", width: str = "700px", **kwargs):
        self.height = height
        self.width = width

        self.__dict__.update(**kwargs)

    def to_dict(self) -> dict:
        return self.__dict__


def convert_networkx_to_agraph(graph: nx.Graph) -> agraph:
    nodes = [Node(id=i, label=i, size=20) for i in graph.nodes()]
    edges = [
        Edge(source=i, target=j, type="CURVE_SMOOTH", label=str(d["weight"]), arrows="")
        for (i, j, d) in graph.edges(data=True)
    ]

    config = UpdatedConfig()

    return_value = agraph(nodes=nodes, edges=edges, config=config)

    return return_value


def init_session_states() -> None:
    if "built" not in st.session_state:
        st.session_state.built = False
    if "serialized" not in st.session_state:
        st.session_state.serialized = False
    if "current_graph" not in st.session_state:
        st.session_state.current_graph = None
    if "info" not in st.session_state:
        st.session_state.info = None
    if "characters" not in st.session_state:
        st.session_state.characters = None


def json_to_networkx(json_graph: dict) -> nx.Graph:
    graph = nx.cytoscape_graph(json_graph)

    return graph
