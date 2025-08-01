from datetime import datetime

import pandas as pd

from config.settings import OUTPUT_TABLE_PATTERN


def generate_table_name(key_name):
    return OUTPUT_TABLE_PATTERN.replace("[REPORT_TYPE]", key_name)


def annotate_table_name(raw_data):
    _raw_data = {}
    for k, v in raw_data.items():
        _raw_data[generate_table_name(k)] = v

    return _raw_data


def transform(raw_data):
    for name, table in raw_data.items():
        raw_data[name] = pd.concat(table, ignore_index=True)
        raw_data[name]["timestamp_created_utc"] = datetime.now()
        if "index" in raw_data[name].columns.to_list():
            raw_data[name].drop(columns={"index"}, inplace=True)

        if "trades" in name:
            raw_data[name]["GrossTradePrice"] = (
                raw_data[name]["GrossTradePrice"]
                .astype(str)
                .str.replace(",", "", regex=False)
                .replace({"": None, "nan": None})
            )

    raw_data = annotate_table_name(raw_data)
    return raw_data
