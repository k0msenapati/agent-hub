from mindsdb import run_query

"""
Data source management module for MindsDB.

This module provides functionality to create and manage data source connections within the MindsDB platform.
Data sources are used to connect to external databases and integrate their data into MindsDB workflows.
"""


def create_datasource(
    datasource_name: str, engine: str, parameters: dict, username: str
) -> None:
    """
    Create a data source connection with the specified parameters, prefixed internally with the username.

    Args:
        datasource_name: The name of the data source to create.
        engine: The database engine type (e.g., 'postgres', 'mysql').
        parameters: A dictionary containing connection parameters like host, port, database, user, password, etc.
        username: The username to prefix the data source name internally.
    """
    internal_name = f"{username}_{datasource_name}"
    params_str = ", ".join([f'"{key}": "{value}"' for key, value in parameters.items()])
    query = f"""
    CREATE DATABASE {internal_name}
    WITH ENGINE = '{engine}',
    PARAMETERS = {{{params_str}}};
    """
    try:
        run_query(query)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            # Retry once if event loop is closed
            run_query(query)
        else:
            raise


def delete_datasource(datasource_name: str, username: str) -> None:
    """
    Delete a data source connection by its name, prefixed internally with the username.

    Args:
        datasource_name: The name of the data source to delete.
        username: The username prefix used internally for the data source name.
    """
    internal_name = f"{username}_{datasource_name}"
    query = f"DROP DATABASE {internal_name};"
    run_query(query)


def list_datasources(username: str) -> list:
    """
    List all data sources for a specific user, filtering by username prefix and returning only the data source names.

    Args:
        username: The username to filter data sources by.

    Returns:
        A list of data source names without the username prefix.
    """
    query = "SHOW DATABASES;"
    result = run_query(query)
    if not result.empty:
        prefix = f"{username}_"
        possible_columns = [
            col for col in result.columns if col.lower().startswith("database")
        ]
        if possible_columns:
            db_column = possible_columns[0]
            return [
                db_name[len(prefix) :]
                for db_name in result[db_column]
                if isinstance(db_name, str)
                and db_name.startswith(prefix)
                and not db_name.endswith("project")
            ]
        else:
            print(
                "No database column found in result. Available columns:", result.columns
            )
    return []


def list_columns(table_name: str, datasource_name: str, username: str) -> list:
    """
    List all columns in a specified table within a data source for a specific user.

    Args:
        table_name: The name of the table to list columns from.
        datasource_name: The name of the data source to list tables from.
        username: The username prefix used internally for the data source name.

    Returns:
        A list of (column name, column type) tuples from the specified table.
    """
    internal_name = f"{username}_{datasource_name}"
    query = f"SHOW COLUMNS FROM {internal_name}.{table_name};"
    result = run_query(query)
    if not result.empty:
        return list(zip(result["Field"], result["Type"]))
    return []


def list_tables(datasource_name: str, username: str) -> list:
    """
    List all tables in a specified data source for a specific user.

    Args:
        datasource_name: The name of the data source to list tables from.
        username: The username prefix used internally for the data source name.

    Returns:
        A list of table names from the specified data source.
    """
    internal_name = f"{username}_{datasource_name}"
    query = f"SHOW TABLES FROM {internal_name};"
    result = run_query(query)
    if not result.empty:
        return list(result[f"Tables_in_{internal_name}"])
    return []
