from datetime import datetime

from database import MSSQLDatabase


def init_db_instance():
    return MSSQLDatabase()


def get_latest_date():
    conn = init_db_instance()
    query = """
    SELECT TOP 1 t.BusinessDate
            FROM (
                SELECT DISTINCT [BusinessDate]
                FROM [etl].[gpp_unsettledtrades]
                UNION
                SELECT DISTINCT [BusinessDate]
                FROM [etl].[gpp_settledtrades]
            ) t
            ORDER BY BusinessDate DESC
    """
    date = conn.select_table(query)["BusinessDate"].to_list()[0]
    return date
