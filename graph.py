from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from state import NewsLetterState

from nodes.planner import planner_node
from nodes.discovery_agent import discovery_agent_node
from nodes.news_agent import news_agent_node
from nodes.startup_agent import startup_agent_node
from nodes.people_agent import people_agent_node
from nodes.github_agent import github_agent_node
from nodes.paper_agent import paper_agent_node
from nodes.reducer import reducer_node
from nodes.writer import writer_node
from nodes.exporter import exporter_node
from nodes.image_agent import image_agent_node
from nodes.email_agent import email_node

def fanout(state: NewsLetterState):

    return [
        Send("news_agent", state),
        Send("startup_agent", state),
        Send("people_agent", state),
        Send("github_agent", state),
        Send("paper_agent", state),
    ]


graph = StateGraph(NewsLetterState)

# Nodes
graph.add_node("planner", planner_node)
graph.add_node("discovery_agent", discovery_agent_node)
graph.add_node("writer", writer_node)
graph.add_node("image_agent", image_agent_node)
graph.add_node("news_agent", news_agent_node)
graph.add_node("startup_agent", startup_agent_node)
graph.add_node("people_agent", people_agent_node)
graph.add_node("github_agent", github_agent_node)
graph.add_node("paper_agent", paper_agent_node)
graph.add_node("email", email_node)
graph.add_node("reducer", reducer_node)
graph.add_node("exporter", exporter_node)


# Planner → Discovery
graph.add_edge(START, "planner")
graph.add_edge("planner", "discovery_agent")


# Discovery → FIVE PARALLEL AGENTS
graph.add_conditional_edges(
    "discovery_agent",
    fanout,
)


# FIVE AGENTS → Reducer
graph.add_edge("news_agent", "reducer")
graph.add_edge("startup_agent", "reducer")
graph.add_edge("people_agent", "reducer")
graph.add_edge("github_agent", "reducer")
graph.add_edge("paper_agent", "reducer")


# Reducer → END
graph.add_edge("reducer", "image_agent")
graph.add_edge("image_agent", "writer")
graph.add_edge("writer", "exporter")
graph.add_edge("exporter", "email")
graph.add_edge("email", END)


app = graph.compile()