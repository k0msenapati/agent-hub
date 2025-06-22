from mindsdb import run_query, server
from mindsdb.queries import SUMMARY_KB, SUMMARY_QUERY_KB


def summarize_kb(project_name: str, kb_name: str, content: str = "") -> str:
    """
    Summarizes the knowledge base content.

    Args:
        project_name (str): The name of the project.
        kb_name (str): The name of the knowledge base.
        content (str, optional): The content to summarize. Defaults to an empty string.

    Returns:
        str: The summary of the knowledge base content.
    """
    summary_query = SUMMARY_QUERY_KB.format(
        project_name=project_name, kb_name=kb_name, content=content
    )
    df = None
    try:
        df = run_query(summary_query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            df = run_query(summary_query)
        else:
            raise

    text = df["content"].str.cat(sep="\n").replace('"', "").replace("'", "")
    summary_df = run_query(SUMMARY_KB.format(kb_content=text))
    return (
        summary_df["summary"].iloc[0]
        if not summary_df.empty
        else "No summary available."
    )
