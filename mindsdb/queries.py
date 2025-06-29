"""
Query templates module for MindsDB.

This module contains predefined SQL query templates used for various operations within the MindsDB platform.
These templates are formatted and executed by other modules to interact with databases, knowledge bases, and agents.
"""

GET_FILE = "SELECT * FROM files.`{file_name}`"

DELETE_FILE = "DROP TABLE files.`{file_name}`"

LIST_FILES = """
SHOW TABLES FROM files
WHERE Tables_in_files LIKE "{name}%"
"""

# CREATE_KB = """
# CREATE KNOWLEDGE_BASE {kb_name}
# USING
#     embedding_model = {embedding_model},
#     reranking_model = {reranking_model},
#     metadata_columns = {metadata_columns},
#     content_columns = {content_columns},
#     id_column = {id_column};
# """

CREATE_INDEX_ON_KB = "CREATE INDEX ON KNOWLEDGE_BASE {kb_name};"

DESCRIB_KB = "DESCRIBE KNOWLEDGE_BASE {kb_name};"

DELETE_KB = "DROP KNOWLEDGE_BASE {kb_name};"

INGEST_DATA = """
INSERT INTO {kb_name}
SELECT *
FROM {table_name};
"""

QUERY_KB = """
SELECT *
FROM {kb_name}
WHERE content = {content}
AND relevance >= {relevance}
{conditions}
"""

CREATE_AGENT = """
CREATE AGENT {agent_name}
USING
    model = '{model_name}',
    {provider}_api_key= '{api_key}',
    include_knowledge_bases = {knowledge_bases},
    prompt_template = '{system_prompt}';
"""

DELETE_AGENT = "DROP AGENT {agent_name};"

QUERY_AGENT = """
SELECT answer
FROM {agent_name} 
WHERE question = '{query}';
"""

SUMMARY_QUERY_KB = """
SELECT CONCAT(chunk_content, metadata) AS `content`
FROM {project_name}.{kb_name}
WHERE content = "{content}"
ORDER BY relevance DESC
LIMIT 5;
"""

SUMMARY_KB = """
SELECT summary
FROM kb_summarizer
WHERE kb_content="{kb_content}";
"""

CREATE_JOB = """
CREATE JOB IF NOT EXISTS {project_name}.{job_name} AS (
    INSERT INTO {project_name}.{kb_name} (
        SELECT 
            {columns}
        FROM {data_source}.{table_name}
        WHERE {id_column} > COALESCE(LAST, (SELECT MAX(id) FROM {project_name}.{kb_name}))
    )
)
EVERY {mins} minutes;
"""

DROP_JOB = """
DROP JOB IF EXISTS {project_name}.{job_name};
"""

EVALUATE_KB_GENERATE = """
EVALUATE KNOWLEDGE_BASE {project_name}.{kb_name}
USING
    test_table = files.{kb_name}_test_data, 
    generate_data = {{'from_sql': 'SELECT chunk_content as content FROM {project_name}.{kb_name}', 'count': 10}}, 
    evaluate = false,
    version = 'llm_relevancy',
    llm = {llm_config};
"""

EVALUATE_KB = """
EVALUATE KNOWLEDGE_BASE {project_name}.{kb_name}
USING
    test_table = files.{kb_name}_test_data, 
    evaluate = true,
    version = 'llm_relevancy',
    llm = {llm_config};
"""
