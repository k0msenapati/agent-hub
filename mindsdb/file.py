from mindsdb import run_query, server
from pandas import DataFrame

from mindsdb.queries import DELETE_FILE, GET_FILE, LIST_FILES

"""
File management module for MindsDB.

This module facilitates interaction with the 'files' database in MindsDB, enabling operations
such as listing, creating, retrieving, and deleting files. These operations are essential for
managing data sources and integrating file-based data into MindsDB workflows.
"""

files_db = server.get_database("files")


def list_files(name: str = "") -> list:
    """
    List all files in the 'files' database that start with the given name.
    
    Args:
        name: The prefix to filter files by name. If empty, lists all files.
        
    Returns:
        A list of file names from the 'files' database matching the given prefix.
    """
    query = LIST_FILES.format(name=name)
    return list(run_query(query)["Tables_in_files"])


def create_file(file_name: str, df: DataFrame, replace: bool = False) -> None:
    """
    Add a file to the 'files' database.
    
    Args:
        file_name: The name of the file to create in the database.
        df: The pandas DataFrame containing the data to store as a file.
        replace: If True, replaces an existing file with the same name. Defaults to False.
    """
    files_db.create_table(name=file_name, query=df, replace=replace)


def get_file(file_name: str) -> DataFrame:
    """
    Retrieve a file from the 'files' database by its name.
    
    Args:
        file_name: The name of the file to retrieve from the database.

    Returns:
        A pandas DataFrame containing the data of the specified file.
    """
    return run_query(GET_FILE.format(file_name=file_name))


def delete_file(file_name: str) -> None:
    """
    Delete a file from the 'files' database by its name.
    
    Args:
        file_name: The name of the file to delete from the database.
    """
    run_query(DELETE_FILE.format(file_name=file_name))
