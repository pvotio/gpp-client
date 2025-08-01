from decouple import config

to_list = lambda x: x.strip().replace(" ", "").split(",")  # noqa: E731


LOG_LEVEL = config("LOG_LEVEL", default="INFO")
OUTPUT_TABLE_PATTERN = config(
    "OUTPUT_TABLE_PATTERN", default="etl.gpp_[REPORT_TYPE]_temp"
)
FETCH_LAST_X_DAYS = config("FETCH_LAST_X_DAYS", cast=int, default=5)
KEEP_REPORT_TYPES = config(
    "KEEP_REPORT_TYPES", cast=to_list, default="settledtrades, unsettledtrades"
)
INSERTER_MAX_RETRIES = config("INSERTER_MAX_RETRIES", cast=int, default=3)
SFTP_HOST = config("SFTP_HOST")
SFTP_PORT = config("SFTP_PORT", cast=int)
SFTP_USER = config("SFTP_USER")
SFTP_PASSWORD = config("SFTP_PASSWORD")
MSSQL_AD_LOGIN = config("MSSQL_AD_LOGIN", cast=bool, default=False)
MSSQL_SERVER = config("MSSQL_SERVER")
MSSQL_DATABASE = config("MSSQL_DATABASE")

if not MSSQL_AD_LOGIN:
    MSSQL_USERNAME = config("MSSQL_USERNAME")
    MSSQL_PASSWORD = config("MSSQL_PASSWORD")
