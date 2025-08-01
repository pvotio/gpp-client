import os
from datetime import datetime, timedelta

import pandas as pd

from config import logger


class Engine:

    DIR = "/Reports"

    def __init__(self, sftp, transport, keep_report_types, fetch_last_x_days):
        self.sftp = sftp
        self.transport = transport
        self.keep_report_types = keep_report_types
        self.fetch_last_x_days = fetch_last_x_days
        self.sftp_files = []
        self.raw_data = {}

    def fetch(self):
        logger.info("Fetching files started")
        self.load_sftp_files()
        self.skip_processed_files()
        if not self.sftp_files:
            logger.warning("No recent reports file detected on SFTP server")
            return False

        self.read_sftp_files()
        if not len(self.raw_data):
            return False

        self.filter_fetched_report()
        logger.info("Fetching files completed")
        return self.raw_data

    def load_sftp_files(self):
        logger.info("Loading SFTP CSV files from directory: %s", self.DIR)
        self.sftp_files = [x for x in self.sftp.listdir(self.DIR) if x.endswith(".csv")]
        logger.info("Total reports file on SFTP server: %d", len(self.sftp_files))
        return

    def skip_processed_files(self):
        try:
            files = []
            logger.info("Fetching data for last %d days", self.fetch_last_x_days)
            date = datetime.now() - timedelta(days=self.fetch_last_x_days)
            logger.info(f"Fetching files from {date} to {datetime.now()} (now)")
            for csv in self.sftp_files:
                _date = datetime.strptime(csv.split("_")[0], "%Y%m%d")
                if _date > date:
                    files.append(csv)

            self.sftp_files = files
        except Exception as e:
            logger.error(f"Error fetching or processing latest date: {str(e)}")
            return False

    def read_sftp_files(self):
        fcount = 0
        logger.info("Reading SFTP CSV files from directory: %s", self.DIR)
        for fname in self.sftp_files:
            try:
                report_type = self.get_report_type(fname)
                df = pd.read_csv(self.sftp.open(os.path.join(self.DIR, fname)))
                df = df[~df.iloc[:, 0].astype(str).str.contains("NO DATA")]
                df.reset_index(inplace=True)
                if report_type not in self.raw_data:
                    self.raw_data[report_type] = []

                self.raw_data[report_type].append(df)
                fcount += 1
            except Exception as e:
                logger.error("Error loading %s: %s", fname, e)
                continue

        logger.info("Total reports files loaded: %d", fcount)
        logger.info("Reading files completed")
        return

    def filter_fetched_report(self):
        _raw_data = {}
        all_reports_types = list(self.raw_data.keys())
        logger.info("Collected reports' types: %s", ", ".join(all_reports_types))
        logger.info("Filtering collected reports")
        if not any([rt in self.raw_data for rt in self.keep_report_types]):
            logger.error(
                "%s not found in %s", self.keep_report_types, all_reports_types
            )
            raise ValueError("Reports type not found in server output")

        for report_type in self.keep_report_types:
            if report_type not in all_reports_types:
                logger.warning("%s report type not found in server output", report_type)
                continue

            _raw_data[report_type] = self.raw_data[report_type]
        self.raw_data = _raw_data
        logger.info(
            "Filtered reports' types: %s", ", ".join(list(self.raw_data.keys()))
        )
        logger.info("Filtering files completed")

    def close(self):
        if self.sftp:
            self.sftp.close()

        if self.transport:
            self.transport.close()

    @staticmethod
    def get_report_type(name):
        return name.split("_")[-1].split(".")[0].lower()
