from typing import Literal, Optional
from pydantic import BaseModel
from mindsdb import run_query
from mindsdb.queries import CREATE_AGENT, DELETE_AGENT, QUERY_AGENT

"""
Agent management module for MindsDB.

This module provides functionality to create, delete, and query agents within the MindsDB platform.
Agents are used to interact with models and knowledge bases to process queries and return answers.
"""


class ModelConfig(BaseModel):
    provider: Literal["openai"] | Literal["anthropic"] | Literal["google"]
    model_name: str
    api_key: str
    system_prompt: str


def create_agent(
    agent_name: str,
    model_config: ModelConfig,
    knowledge_bases: Optional[list[str]] = None,
    project_name: str = "mindsdb"
) -> None:
    """
    Create an agent with the specified configuration and associated knowledge bases.

    Args:
        agent_name: The name of the agent to create.
        model_config: Configuration for the model including provider, model name, API key, and system prompt.
        knowledge_bases: Optional list of knowledge base names to associate with the agent.
        project_name: The name of the project associated with the agent. Defaults to 'mindsdb'.
    """
    if not knowledge_bases:
        raise Exception("Cant create agent without kbs")
    
    query = CREATE_AGENT.format(
        agent_name=f"{project_name}.{agent_name}",
        model_name=model_config.model_name,
        provider=model_config.provider,
        api_key=model_config.api_key,
        knowledge_bases=knowledge_bases,
        system_prompt=model_config.system_prompt,
    )
    run_query(query)


def delete_agent(agent_name: str, project_name: str = "mindsdb") -> None:
    """
    Delete an agent by its name.

    Args:
        agent_name: The name of the agent to delete.
        project_name: The name of the project associated with the agent. Defaults to 'mindsdb'.
    """
    query = DELETE_AGENT.format(agent_name=f"{project_name}.{agent_name}")
    run_query(query)


def query_agent(agent_name: str, question: str, project_name: str = "mindsdb") -> str:
    """
    Query an agent with a specific question and return the answer.

    Args:
        agent_name: The name of the agent to query.
        question: The question to ask the agent.
        project_name: The name of the project associated with the agent. Defaults to 'mindsdb'.

    Returns:
        The answer from the agent as a string.
    """
    query = QUERY_AGENT.format(
        agent_name=f"{project_name}.{agent_name}", query=question.replace("'", "\\'")
    )
    try:
        result = run_query(query)
        return result["answer"].iloc[0] if not result.empty else ""
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            result = run_query(query)
            return result["answer"].iloc[0] if not result.empty else ""
        else:
            raise
