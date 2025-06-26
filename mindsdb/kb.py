from typing import Literal, Optional, Union

from pandas import DataFrame
from mindsdb import run_query
from pydantic import BaseModel, Field

from mindsdb.queries import CREATE_INDEX_ON_KB, CREATE_JOB, DELETE_KB, DESCRIB_KB, DROP_JOB, INGEST_DATA, QUERY_KB, EVALUATE_KB, EVALUATE_KB_GENERATE

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
    create_query = f"""
    CREATE KNOWLEDGE BASE {project_name}.{config.name}
    USING
        embedding_model = {config.embedding_model.model_dump_json()},
        {"reranking_model = " + config.reranking_model.model_dump_json() + "," if config.reranking_model else ""}
        storage = pvec.{config.name}_storage,
        metadata_columns = {config.metadata_columns},
        content_columns = {config.content_columns},
        id_column = '{config.id_column}'
    """
    try:
        run_query(create_query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            run_query(create_query)
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
    index_query = CREATE_INDEX_ON_KB.format(kb_name=f"{project_name}.{kb_name}")
    run_query(index_query)


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

def create_job(
    job_name: str, kb_name: str, data_source: str, table_name: str, columns: str, id_column: str, minutes: int = 10, project_name: str = "mindsdb"
) -> None:
    """
    Create a job for automated ingestion of records into a knowledge base from a data source.
    
    Args:
        job_name: The name of the job to create.
        kb_name: The name of the knowledge base to ingest data into.
        data_source: The name of the data source to fetch records from.
        table_name: The name of the table in the data source to fetch records from.
        columns: The columns to select from the table.
        id_column: The column used to track the last ingested record.
        minutes: The interval in minutes for the job to run. Defaults to 10.
        project_name: The name of the project associated with the knowledge base. Defaults to 'mindsdb'.
    """
    query = CREATE_JOB.format(
        project_name=project_name,
        job_name=job_name,
        kb_name=kb_name,
        data_source=data_source,
        table_name=table_name,
        columns=columns,
        id_column=id_column,
        mins=minutes
    )
    print(query)
    run_query(query)

def drop_job(job_name: str, project_name: str = "mindsdb") -> None:
    """
    Drop a job by its name.
    
    Args:
        job_name: The name of the job to drop.
        project_name: The name of the project associated with the job. Defaults to 'mindsdb'.
    """
    query = DROP_JOB.format(project_name=project_name, job_name=job_name)
    run_query(query)


def evaluate_knowledge_base(
    kb_name: str, 
    project_name: str = "mindsdb", 
    evaluate: bool = False, 
    llm_config: dict | None = None
) -> DataFrame:
    """
    Evaluate a knowledge base, either generating test data or running the evaluation.
    
    Args:
        kb_name: The name of the knowledge base to evaluate.
        project_name: The name of the project associated with the knowledge base. Defaults to 'mindsdb'.
        evaluate: Boolean indicating whether to generate test data (False) or run evaluation (True). Defaults to False.
        llm_config: Dictionary containing LLM configuration details. If None, it will be fetched from environment or user input.
        
    Returns:
        A pandas DataFrame containing the results of the evaluation or generation process.
    """
    if llm_config is None:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        llm_config = {
            'provider': 'openai',
            'base_url': 'https://api.groq.com/openai/v1',
            'api_key': os.getenv("GROQ_API_KEY", ""),
            'model_name': 'qwen/qwen3-32b'
        }
    
    query_template = EVALUATE_KB if evaluate else EVALUATE_KB_GENERATE
    query = query_template.format(
        project_name=project_name,
        kb_name=kb_name,
        llm_config=llm_config
    )
    try:
        return run_query(query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            return run_query(query)
        else:
            raise
