from langgraph.graph import StateGraph, END
from src.config import MAX_ITERATIONS
from src.agents.state import AgentState
from src.agents.nodes import (
    deconstruct_jd_node,
    synthesize_projects_node,
    evaluate_portfolio_node,
    generate_artifacts_node,
)


def route_evaluation(state: AgentState) -> str:
    """
    Conditional evaluation router:
      - Routes to 'generate_artifacts' if portfolio passes all gates
      - Routes to 'generate_artifacts' if iteration count >= MAX_ITERATIONS (safety brake)
      - Otherwise cycles back to 'synthesize_projects' with critique feedback
    """
    eval_data = state.get("evaluation_result")
    if eval_data and eval_data.passed_all_gates:
        return "generate_artifacts"

    iteration_count = state.get("iteration_count", 0)
    if iteration_count >= MAX_ITERATIONS:
        return "generate_artifacts"  # Cap iterations to prevent infinite loop

    return "synthesize_projects"


def create_resume_graph():
    """Compiles and returns the cyclical LangGraph resume generation graph."""
    builder = StateGraph(AgentState)

    builder.add_node("deconstruct_jd", deconstruct_jd_node)
    builder.add_node("synthesize_projects", synthesize_projects_node)
    builder.add_node("evaluate_portfolio", evaluate_portfolio_node)
    builder.add_node("generate_artifacts", generate_artifacts_node)

    builder.set_entry_point("deconstruct_jd")
    builder.add_edge("deconstruct_jd", "synthesize_projects")
    builder.add_edge("synthesize_projects", "evaluate_portfolio")

    builder.add_conditional_edges(
        "evaluate_portfolio",
        route_evaluation,
        {
            "generate_artifacts": "generate_artifacts",
            "synthesize_projects": "synthesize_projects",
        },
    )
    builder.add_edge("generate_artifacts", END)

    return builder.compile()
