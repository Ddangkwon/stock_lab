import os
import subprocess
import sys
import json
import numpy as np
import pandas as pd
import FinanceDataReader as fdr
from stock_analysis import  *
VERSION = '0.0.1'


def generate_tickers_json():
    ticker_company_dict = {
        '259960.KS': '크래프톤',
        '000270.KS': '기아자동차',
        '005930.KS': '삼성전자',
        '000660.KS': 'SK하이닉스',
        '011200.KS': 'HMM',
        '012330.KS': '현대모비스',
        '005935.KS': '삼성전자우',
        '005380.KS': '현대차',
        '051900.KS': 'LG화학',
        '035420.KS': 'NAVER',
        '207940.KS': '삼성바이오로직스',
        '005490.KS': 'POSCO',
        '006400.KS': '삼성SDI',
        '028260.KS': '삼성물산',
        '051910.KS': 'LG화학',
        '017670.KS': 'SK텔레콤',
        '015760.KS': '한국전력',
        '055550.KS': '신한지주',
        '105560.KS': 'KB금융',
        '034730.KS': 'SK이노베이션',
        '032830.KS': '삼성생명',
        '011170.KS': '롯데케미칼',
        '096770.KS': 'SK이노베이션',
        '000810.KS': '삼성화재',
        '000660.KS': 'SK하이닉스',
        '018260.KS': '삼성에스디에스',
        '003550.KS': 'LG',
        '086790.KS': '하나금융지주',
        '010950.KS': 'S-Oil',
        '251270.KS': '넷마블',
        '030200.KS': 'KT',
        '009150.KS': '삼성전기',
        '032640.KS': 'LG유플러스',
        '033780.KS': 'KT&G',
        '035720.KS': '카카오',
        '000270.KS': '기아자동차',
        '012330.KS': '현대모비스',
        '028050.KS': '삼성엔지니어링',
        '316140.KS': '우리금융지주',
        '000720.KS': '현대건설',
        '086280.KS': '현대글로비스',
        '004020.KS': '현대제철',
        '011200.KS': 'HMM',
        '009540.KS': '현대중공업지주',
        '035250.KS': '강원랜드',
        '011780.KS': '금호석유',
        '010130.KS': '고려아연',
        '030000.KS': '제일기획',
        '004990.KS': '롯데지주',
        '024110.KS': '기업은행',
        '002790.KS': '아모레G',
        '004990.KS': '롯데지주',
        '009830.KS': '한화솔루션',
        '051910.KS': 'LG에너지솔루션',
        '066570.KS': 'LG전자',
        '011070.KS': 'LG이노텍',
        '000880.KS': '한화',
        '272210.KS': '한화시스템',
        '012200.KS': '계양전기',
        '019490.KS': 'HL만도',
        '018880.KS': '한온시스템',
        '352820.KS': '하이브',
        '047810.KS': '한국항공우주',
        '079550.KS': 'LIG넥스원',
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOG': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        # 다른 주식들의 정보는 생략했습니다.
    }

    with open('./Ticker.json', 'w') as f:
        json.dump(ticker_company_dict, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    generate_tickers_json()

    with open('./Ticker.json', "r") as json_file:
        json_data = json.load(json_file)

    analyzer = StockAnalyzer(json_data)
    analyzer.analyze_stocks()