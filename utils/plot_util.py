import subprocess
import sys


class StockItem(object):
    def __init__(self):
        try:
            import pandas_datareader.data as stdata
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", 'pandas_datareader'])
        finally:
            import pandas_datareader.data as stdata

    def load_stock(self, item):
        df = stdata.DataReader(item, 'yahoo')
        df = df.reset_index()

        return df

    def print_item(self, item):
        self.load_stock(item)