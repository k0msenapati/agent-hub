from typing import Literal, Optional, Union

from pandas import DataFrame
from mindsdb import run_query
from pydantic import BaseModel, Field

from mindsdb.queries import DELETE_KB, DESCRIB_KB, INGEST_DATA, QUERY_KB

"""
Knowledge base management module for MindsDB.

This module provides functionality to create, manage, and query knowledge bases within the MindsDB platform.
Knowledge bases are used to store and retrieve structured information for use in AI models and agents.
"""


class OpenAIEmbeddingModel(BaseModel):
    provider: Literal["openai"]
    model_name: str
    api_key: str
    base_url: Optional[str] = None


class OllamaEmbeddingModel(BaseModel):
    provider: Literal["ollama"]
    model_name: str
    base_url: str


EmbeddingModel = Union[OpenAIEmbeddingModel, OllamaEmbeddingModel]
ReRankingModel = OpenAIEmbeddingModel


class KnowledgeBaseConfig(BaseModel):
    name: str
    embedding_model: EmbeddingModel
    reranking_model: Optional[ReRankingModel] = None
    metadata_columns: list[str] = Field(default_factory=list)
    content_columns: list[str] = Field(default_factory=list)
    id_column: str = Field(
        ..., description="The name of the column containing document IDs."
    )


def create_knowledge_base(config: KnowledgeBaseConfig, project_name: str = "mindsdb") -> None:
    """
    Create a knowledge base with the given configuration.
    
    Args:
        config: A KnowledgeBaseConfig object containing the configuration for the knowledge base,
                including embedding model, reranking model, and column specifications.
        project_name: The name of the project to associate with the knowledge base. Defaults to 'mindsdb'.
    """
    query = f"""
    CREATE KNOWLEDGE BASE {project_name}.{config.name}
    USING
        embedding_model = {config.embedding_model.model_dump_json()},
        {"reranking_model = " + config.reranking_model.model_dump_json() + "," if config.reranking_model else ""}
        metadata_columns = {config.metadata_columns},
        content_columns = {config.content_columns},
        id_column = '{config.id_column}'
    """
    try:
        run_query(query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            run_query(query)
        else:
            raise


def delete_knowledge_base(kb_name: str, project_name: str = "mindsdb") -> None:
    """
    Delete a knowledge base by its name.
    
    Args:
        kb_name: The name of the knowledge base to delete.
        project_name: The name of the project associated with the knowledge base. Defaults to 'mindsdb'.
    """
    run_query(DELETE_KB.format(kb_name=f"{project_name}.{kb_name}"))


def ingest_data(kb_name: str, table_name: str, project_name: str = "mindsdb") -> None:
    """
    Ingest data into the knowledge base from a specified table.
    
    Args:
        kb_name: The name of the knowledge base to ingest data into.
        table_name: The name of the table containing the data to ingest.
        project_name: The name of the project associated with the knowledge base. Defaults to 'mindsdb'.
    """
    query = INGEST_DATA.format(kb_name=f"{project_name}.{kb_name}", table_name=table_name)
    try:
        run_query(query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            run_query(query)
        else:
            raise


def query_knowledge_base(
    kb_name: str, content: str, relevance: float = 0.2, conditions: Optional[str] = None, project_name: str = "mindsdb"
) -> DataFrame:
    """
    Query the knowledge base and return results with a specified relevance threshold.
    
    Args:
        kb_name: The name of the knowledge base to query.
        content: The content or query text to search for in the knowledge base.
        relevance: The minimum relevance score for returned results. Defaults to 0.2.
        conditions: Optional additional conditions for the query. Defaults to None.
        project_name: The name of the project associated with the knowledge base. Defaults to 'mindsdb'.
        
    Returns:
        A pandas DataFrame containing the query results from the knowledge base.
    """
    query = QUERY_KB.format(
        kb_name=f"{project_name}.{kb_name}",
        content=f"'{content}'",
        relevance=relevance,
        conditions=conditions or "",
    )
    try:
        return run_query(query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            return run_query(query)
        else:
            raise
