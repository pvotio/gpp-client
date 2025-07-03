from datetime import datetime

import pandas as pd


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

    return raw_data
