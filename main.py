from client import Engine
from client.sftp import sftp_session
from config import logger, settings
from database.helper import init_db_instance
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
    engine = Engine(
        sftp, transport, settings.KEEP_REPORT_TYPES, settings.FETCH_LAST_X_DAYS
    )
    raw_data = engine.fetch()
    engine.close()
    if not raw_data:
        logger.warning("No data collected. terminating the application...")
        return

    logger.info("Transforming Data")
    dfs_transformed = transform(raw_data)
    logger.info("Inserting Data into database")
    conn = init_db_instance()
    for name, df in dfs_transformed.items():
        logger.debug(f"{name}:\n{df}")
        logger.info(f"Inserting data to {name}")
        conn.insert_table(df, name, delete_prev_records=True)

    logger.info("Application completed successfully")
    return


if __name__ == "__main__":
    main()
