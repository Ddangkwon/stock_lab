import os
import subprocess
import sys

import numpy as np
import pandas as pd
import FinanceDataReader as fdr

from utils.print_opt import *
from utils.stock_data_loader import *
from stock_analysis_v1 import *
from stock_analysis import  *
VERSION = '0.0.1'

ticker_company_dict = {
    '000270.KS': '기아자동차',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOG': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    '005930.KS': '삼성전자',
    '000660.KS': 'SK하이닉스',
    '011200.KS': 'HMM',
    '012330.KS': '현대모비스',
    # 다른 주식들의 정보는 생략했습니다.
}

class StockLab:
    def __init__(self):
        pass
    def load_krx_stock_data(self):
        stock_data_loader("KRX")


if __name__ == "__main__":
    # # print_g("Version : %s" % VERSION)
    # # SL = StockLab()
    # # krx_data= SL.load_krx_stock_data()
    # import plotly.graph_objects as go
    # import numpy as np
    # from plotly.offline import plot
    # import plotly.io as pio
    #
    # # Generate sample data
    # x = np.linspace(0, 10, 100)
    # y = np.sin(x)
    #
    # # Create a scatter plot
    # fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers'))
    #
    # # Update layout
    # fig.update_layout(
    #     title='Sin Wave',
    #     xaxis_title='X',
    #     yaxis_title='Y'
    # )
    #
    # # Generate an HTML file with the plot
    # plot(fig, filename='plot.html', auto_open=False)
    #
    # # Convert the HTML file to a PDF
    # pio.write_image(fig, 'plot.pdf', format='pdf')
    analyzer = StockAnalyzer(ticker_company_dict)
    analyzer.analyze_stocks()