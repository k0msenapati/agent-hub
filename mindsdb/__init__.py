from mindsdb_sdk import connect
from pandas import DataFrame

"""
MindsDB SDK initialization module.

This module provides the core functionality for connecting to the MindsDB server
and executing queries. It serves as the entry point for interacting with MindsDB's
features through the SDK.
"""

server = connect()

def run_query(query: str) -> DataFrame:
    """
    Execute a query on the MindsDB server and fetch the results.
    
    Args:
        query: The SQL query to execute on the MindsDB server.
        
    Returns:
        A pandas DataFrame containing the results of the query.
    """
    return server.query(query).fetch()
