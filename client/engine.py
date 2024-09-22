import datetime
import os

import pandas as pd

from client.utils import generate_table_name
from config import logger, settings


class Engine:

    DIR = "/Reports"

    def __init__(self, sftp, transport, conn):
        self.sftp = sftp
        self.transport = transport
        self.conn = conn
        self.sftp_files = []
        self.raw_data = {}

    def fetch(self):
        logger.info("Fetching files started.")
        self.load_sftp_files()
        self.skip_processed_files()
        if not self.sftp_files:
            logger.warning("No new csv detected on SFTP server.")
            return False

        self.read_sftp_files()
        if not len(self.raw_data):
            return False

        logger.info("Fetching files completed.")
        return self.raw_data

    def load_sftp_files(self):
        logger.info("Loading SFTP CSV files from directory: %s", self.DIR)
        self.sftp_files = [x for x in self.sftp.listdir(self.DIR) if x.endswith(".csv")]
        logger.info("Total CSVs loaded: %d", len(self.sftp_files))
        return

    def skip_processed_files(self):
        query = """SELECT TOP 1 t.BusinessDate
            FROM (
                SELECT DISTINCT [BusinessDate]
                FROM [etl].[gpp_unsettledtrades]
                UNION
                SELECT DISTINCT [BusinessDate]
                FROM [etl].[gpp_settledtrades]
            ) t
            ORDER BY BusinessDate DESC
        """
        self.conn.db_connection.connect()
        conn = self.conn.db_connection.engine.raw_connection()
        cursor = conn.cursor()
        try:
            res = []
            date = cursor.execute(query).fetchone()[0]
            logger.info(f"Most recent date: {date}")
            for csv in self.sftp_files:
                _date = datetime.strptime(csv.split("_")[0], "%Y%m%d")
                if _date > date:
                    res.append(csv)

            self.sftp_files = res
        except Exception as e:
            logger.error(f"Error fetching or processing latest date: {str(e)}")
            return False

        finally:
            cursor.close()
            conn.close()

    def read_sftp_csvs(self):
        for csv in self.sftp_files:
            table_name = generate_table_name(csv)
            df = pd.read_csv(self.sftp.open(os.path.join(self.DIR, csv)))
            df = df[~df.iloc[:, 0].astype(str).str.contains("NO DATA")]
            df.reset_index(inplace=True)
            if table_name not in self.raw_data:
                self.raw_data[table_name] = []

            self.raw_data[table_name].append(df)

        return

    def close(self):
        if self.sftp:
            self.sftp.close()

        if self.transport:
            self.transport.close()
