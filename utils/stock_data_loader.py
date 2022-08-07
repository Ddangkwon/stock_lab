

import pandas as pd
import FinanceDataReader as fdr


def stock_data_loader(data_name):
    df_data = fdr.StockListing(data_name)
    file_name = "%s.csv" % data_name
    df_data.to_csv(file_name, index=False)
    df_data_csv = pd.read_csv("krx.csv")

    return df_data_csv