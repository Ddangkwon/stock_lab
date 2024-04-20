import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

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


# 여러 주식 데이터 ticker를 저장하는 함수
def save_tickers(tickers):
    with open('tickers.txt', 'w') as file:
        for ticker in tickers:
            file.write(ticker + '\n')


# 저장된 ticker를 불러오는 함수
def load_tickers():
    tickers = []
    with open('tickers.txt', 'r') as file:
        for line in file:
            tickers.append(line.strip())
    return tickers


# 주식 데이터 다운로드
def download_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data, ticker


# 이동평균을 계산하는 함수
def calculate_moving_average(data, window):
    return data['Close'].rolling(window=window).mean()


# 볼린저 밴드 계산 함수
def calculate_bollinger_bands(data, window):
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    upper_band = rolling_mean + (2 * rolling_std)
    lower_band = rolling_mean - (2 * rolling_std)
    return upper_band, lower_band


# 이동평균 교차 전략을 구현하는 함수
def moving_average_cross_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['short_mavg'] = calculate_moving_average(data, short_window)
    signals['long_mavg'] = calculate_moving_average(data, long_window)
    signals['signal'] = 0.0
    signals['signal'][short_window:] = np.where(
        signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()
    return signals


# 전략 수익률 계산
def calculate_returns(signals, data):
    returns = pd.DataFrame(index=data.index)
    returns['price'] = data['Close']
    returns['signal'] = signals['signal']
    returns['positions'] = signals['positions']
    returns['daily_returns'] = returns['price'].pct_change()
    returns['strategy_returns'] = returns['daily_returns'] * returns['signal'].shift(1)
    return returns


# 그래프 그리기
def plot_graph(stock_data, signals, company_name, upper_band, lower_band, pdf, returns):
    plt.figure(figsize=(12, 6))
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    plt.plot(stock_data['Close'], label='Close Price')
    plt.plot(signals['short_mavg'], label='Short Moving Average', color='red')
    plt.plot(signals['long_mavg'], label='Long Moving Average', color='blue')
    plt.plot(signals.loc[signals.positions == 1.0].index,
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='g', lw=0, label='Buy Signal')
    plt.plot(signals.loc[signals.positions == -1.0].index,
             signals.short_mavg[signals.positions == -1.0],
             'v', markersize=10, color='r', lw=0, label='Sell Signal')
    plt.fill_between(stock_data.index, upper_band, lower_band, color='gray', alpha=0.3, label='Bollinger Bands')
    plt.plot(upper_band, linestyle='--', linewidth=1, color='black')
    plt.plot(lower_band, linestyle='--', linewidth=1, color='black')

    # 전략 수익률 플롯
    buy_dates = returns[returns['positions'] == 1.0].index
    sell_dates = returns[returns['positions'] == -1.0].index
    plt.scatter(buy_dates, stock_data.loc[buy_dates]['Close'], marker='^', s=100,color='c', label='Buy Signal')
    plt.scatter(sell_dates, stock_data.loc[sell_dates]['Close'], marker='v', s=100, color='y', label='Sell Signal')

    plt.title(f'Moving Average Crossover Strategy - {company_name}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    pdf.savefig()
    plt.close()


# 메인 함수
def stock_analysis_v1():

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    # 데이터 다운로드 기간 설정
    start_date = '2020-01-01'
    end_date = current_date

    # PDF 파일 설정
    pdf_path = 'result/stock_analysis.pdf'
    pdf = PdfPages(pdf_path)

    for ticker in ticker_company_dict.keys():
        # 주식 데이터 다운로드
        stock_data, company_name = download_stock_data(ticker, start_date, end_date)

        # 이동평균 교차 전략 파라미터 설정
        short_window = 50
        long_window = 200

        # 이동평균 교차 전략 계산
        signals = moving_average_cross_strategy(stock_data, short_window, long_window)

        # 볼린저 밴드 계산
        upper_band, lower_band = calculate_bollinger_bands(stock_data, short_window)

        # 전략 수익률 계산
        returns = calculate_returns(signals, stock_data)

        # 그래프 그리기
        plot_graph(stock_data, signals, ticker_company_dict[ticker], upper_band, lower_band, pdf, returns)

        # 선택된 ticker 출력
        print(f"{ticker_company_dict[ticker]} 주식 데이터의 Ticker: {ticker}")

    # PDF 파일 닫기
    pdf.close()


if __name__ == "__main__":
    stock_analysis_v1()
