from client import Engine
from client.sftp import sftp_session
from config import logger, settings
from database.helper import create_inserter_objects
from transformer import transform


def main():
    logger.info("Initializing GPP Client Engine")
    sftp, transport = sftp_session(
        host=settings.SFTP_HOST,
        port=settings.SFTP_PORT,
        username=settings.SFTP_USER,
        password=settings.SFTP_PASSWORD,
    )
    logger.info("Preparing Database Connection")
    conn = create_inserter_objects(
        server=settings.MSSQL_SERVER,
        database=settings.MSSQL_DATABASE,
        username=settings.MSSQL_USERNAME,
        password=settings.MSSQL_PASSWORD,
    )
    engine = Engine(sftp, transport, conn)
    raw_data = engine.fetch()
    engine.close()
    if not raw_data:
        logger.warning("No data collected. terminating the application...")
        return

    logger.info("Transforming Data")
    dfs_transformed = transform(raw_data)
    logger.info("Inserting Data into database")
    for name, df in dfs_transformed.items():
        logger.debug(f"{name}:\n{df}")
        logger.info(f"Inserting data to {name}")
        conn.insert(df, name)

    logger.info("Application completed successfully")
    return


if __name__ == "__main__":
    main()
