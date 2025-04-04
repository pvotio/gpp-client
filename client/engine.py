import os
from datetime import datetime

import pandas as pd

from client.utils import generate_table_name
from config import logger
from database.helper import get_latest_date


class Engine:

    DIR = "/Reports"

    def __init__(self, sftp, transport):
        self.sftp = sftp
        self.transport = transport
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
        try:
            res = []
            date = get_latest_date()
            logger.info(f"Most recent date: {date}")
            for csv in self.sftp_files:
                _date = datetime.strptime(csv.split("_")[0], "%Y%m%d")
                if _date > date:
                    res.append(csv)

            self.sftp_files = res
        except Exception as e:
            logger.error(f"Error fetching or processing latest date: {str(e)}")
            return False

    def read_sftp_files(self):
        logger.info("Reading SFTP CSV files from directory: %s", self.DIR)
        for csv in self.sftp_files:
            table_name = generate_table_name(csv)
            df = pd.read_csv(self.sftp.open(os.path.join(self.DIR, csv)))
            df = df[~df.iloc[:, 0].astype(str).str.contains("NO DATA")]
            df.reset_index(inplace=True)
            if table_name not in self.raw_data:
                self.raw_data[table_name] = []

            self.raw_data[table_name].append(df)

        logger.info("Reading SFTP files completed")
        return

    def close(self):
        if self.sftp:
            self.sftp.close()

        if self.transport:
            self.transport.close()
