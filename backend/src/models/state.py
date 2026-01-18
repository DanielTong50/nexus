from typing import TypedDict, List, Annotated, Union, Any
from langchain_core.messages import BaseMessage
import operator

class GraphState(TypedDict):
    """
    Represents the state of the agent graph.

    Attributes:
        messages: The chat history.
        next_step: The next node to route to.
        errors: Any errors encountered during execution.
    """
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    errors: List[str]
