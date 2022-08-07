import os
import subprocess
import sys

import numpy as np
import pandas as pd
import FinanceDataReader as fdr

from utils.print_opt import *
from utils.stock_data_loader import *
VERSION = '0.0.1'


class StockLab:
    def __init__(self):

    def load_krx_stock_data(self):
        stock_data_loader("KRX")


if __name__ == "__main__":
    print_g("Version : %s" % VERSION)
    SL = StockLab()
    krx_data= SL.load_krx_stock_data()