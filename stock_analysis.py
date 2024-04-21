import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import mplfinance as mpf

class MovingAverageRSIStrategy:
    def __init__(self, data, short_window, long_window, rsi_window):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window
        self.rsi_window = rsi_window

    def calculate_moving_average(self):
        self.data['short_mavg'] = self.data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        self.data['long_mavg'] = self.data['Close'].rolling(window=self.long_window, min_periods=1).mean()

    def calculate_rsi(self):
        delta = self.data['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_window, min_periods=1).mean()

        avg_gain = gain.ewm(span=self.rsi_window).mean()
        avg_loss = loss.ewm(span=self.rsi_window).mean()

        rs = avg_gain / avg_loss
        self.data['rsi'] = 100 - (100 / (1 + rs))

    def generate_signals(self):
        self.calculate_moving_average()
        self.calculate_rsi()

        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0.0

        # 이동평균 교차 매매 시그널 생성
        signals['signal'][self.short_window:] = np.where(
            self.data['short_mavg'][self.short_window:] > self.data['long_mavg'][self.short_window:], 1.0, 0.0)

        # RSI 조건 추가
        signals['signal'][(self.data['rsi'] < 30) & (signals['signal'] == 1.0)] = 1.0
        signals['signal'][(self.data['rsi'] > 70) & (signals['signal'] == 1.0)] = 0.0

        # 포지션 변경 시그널 생성
        signals['positions'] = signals['signal'].diff()

        return signals

    def plot_moving_average_rsi_strategy(self, stock_data, signals, company_name, pdf):
        self.calculate_moving_average()  # Ensure moving averages are calculated
        plt.figure(figsize=(12, 6))
        plt.plot(stock_data['Close'], label='Close Price')
        plt.plot(self.data['short_mavg'], label='Short Moving Average', color='red')
        plt.plot(self.data['long_mavg'], label='Long Moving Average', color='blue')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 self.data['short_mavg'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 self.data['short_mavg'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.title(f'Moving Average RSI Strategy - {company_name}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()

class StockAnalyzer:
    def __init__(self, ticker_company_dict):
        self.ticker_company_dict = ticker_company_dict

    def save_tickers(self, tickers):
        with open('tickers.txt', 'w') as file:
            for ticker in tickers:
                file.write(ticker + '\n')

    def load_tickers(self):
        tickers = []
        with open('tickers.txt', 'r') as file:
            for line in file:
                tickers.append(line.strip())
        return tickers

    def download_stock_data(self, ticker, start_date, end_date):
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data, ticker

    def calculate_moving_average(self, data, window):
        return data['Close'].rolling(window=window).mean()

    def calculate_bollinger_bands(self, data, window):
        rolling_mean = data['Close'].rolling(window=window).mean()
        rolling_std = data['Close'].rolling(window=window).std()
        upper_band = rolling_mean + (2 * rolling_std)
        lower_band = rolling_mean - (2 * rolling_std)
        return upper_band, lower_band

    def moving_average_cross_strategy(self, data, short_window, long_window):
        signals = pd.DataFrame(index=data.index)
        signals['short_mavg'] = self.calculate_moving_average(data, short_window)
        signals['long_mavg'] = self.calculate_moving_average(data, long_window)
        signals['signal'] = 0.0
        # 이동평균 크로스오버 전략: 단기 이평이 장기 이평을 상향 돌파하면 1로, 그렇지 않으면 0으로 설정
        signals['signal'][short_window:] = np.where(
            signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
        return signals

    def calculate_returns(self, signals, data):
        returns = pd.DataFrame(index=data.index)
        returns['price'] = data['Close']
        returns['signal'] = signals['signal']
        returns['positions'] = signals['positions']
        returns['daily_returns'] = returns['price'].pct_change()
        returns['strategy_returns'] = returns['daily_returns'] * returns['signal'].shift(1)
        return returns

    def rsi_strategy(self, data, window):
        signals = pd.DataFrame(index=data.index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        RS = gain / loss
        RSI = 100 - (100 / (1 + RS))
        # RSI 전략: RSI가 30 미만이면 과매도 상태로 간주하여 매수 신호 1로 설정
        #           RSI가 70 초과이면 과매수 상태로 간주하여 매도 신호 -1로 설정
        signals['signal'] = np.where(RSI > 70, -1.0, 0.0)  # Sell when RSI is above 70
        signals['signal'] = np.where(RSI < 30, 1.0, signals['signal'])  # Buy when RSI is below 30
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_rsi_strategy(self, stock_data, signals, company_name, pdf):
        plt.figure(figsize=(12, 6))
        plt.plot(stock_data['Close'], label='Close Price')
        plt.title(f'RSI Strategy - {company_name}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        # Plot buy signals
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 stock_data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        # Plot sell signals
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 stock_data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        pdf.savefig()
        plt.close()

    def plot_graph(self, stock_data, signals, company_name, upper_band, lower_band, pdf, returns):
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
        plt.scatter(buy_dates, stock_data.loc[buy_dates]['Close'], marker='^', s=100, color='c', label='Buy Signal(Sub)')
        plt.scatter(sell_dates, stock_data.loc[sell_dates]['Close'], marker='v', s=100, color='y', label='Sell Signal(Sub)')

        plt.title(f'Moving Average Crossover Strategy - {company_name}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()


    def plot_mplfinance(self, stock_data, signals, company_name, upper_band, lower_band, pdf, returns):
        ap_upper = mpf.make_addplot(upper_band, linestyle='--', color='black')
        ap_lower = mpf.make_addplot(lower_band, linestyle='--', color='black')
        ap_short_mavg = mpf.make_addplot(signals['short_mavg'], color='red')
        ap_long_mavg = mpf.make_addplot(signals['long_mavg'], color='blue')

        # Create a figure and plot the data
        fig, ax = mpf.plot(stock_data, type='candle', addplot=[ap_upper, ap_lower, ap_short_mavg, ap_long_mavg],
                           title=f'Moving Average Crossover Strategy - {company_name}', volume=False, style='charles',
                           warn_too_much_data=1000000, returnfig=True)
        # Save the figure to the PDF
        pdf.savefig(fig)


    def analyze_stocks(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        # 데이터 다운로드 기간 설정
        start_date = '2020-01-01'
        end_date = current_date

        # 이동평균선 정략
        pdf_path = 'result/stock_analysis.pdf'
        pdf = PdfPages(pdf_path)
        # mplfinance 패키지 사용 출력
        pdf_path_v2 = 'result/stock_analysis_v2.pdf'
        pdf_v2 = PdfPages(pdf_path_v2)
        # rsi 전략
        pdf_path_v3 = 'result/stock_analysis_v3.pdf'
        pdf_v3 = PdfPages(pdf_path_v3)
        # 이동평균선 + rsi
        pdf_path_v4 = 'result/stock_analysis_v4.pdf'
        pdf_v4 = PdfPages(pdf_path_v4)
        for ticker in self.ticker_company_dict.keys():
            # 주식 데이터 다운로드
            stock_data, company_name = self.download_stock_data(ticker, start_date, end_date)

            # 이동평균 교차 전략 파라미터 설정
            short_window = 50
            long_window = 200

            # 이동평균 교차 전략 계산
            signals = self.moving_average_cross_strategy(stock_data, short_window, long_window)

            # 볼린저 밴드 계산
            upper_band, lower_band = self.calculate_bollinger_bands(stock_data, short_window)

            # 전략 수익률 계산
            returns = self.calculate_returns(signals, stock_data)

            self.plot_graph(stock_data, signals, self.ticker_company_dict[ticker], upper_band, lower_band, pdf, returns)
            # Plot using mplfinance
            self.plot_mplfinance(stock_data, signals, self.ticker_company_dict[ticker], upper_band, lower_band,
                                 pdf_v2, returns)

            # RSI 전략 계산
            signals_rsi = self.rsi_strategy(stock_data, window=14)
            self.plot_rsi_strategy(stock_data, signals_rsi, self.ticker_company_dict[ticker], pdf_v3)
            # MovingAverageRSIStrategy 클래스의 인스턴스 생성
            signals_ma_rsi_strategy = MovingAverageRSIStrategy(stock_data, short_window=50, long_window=200,
                                                               rsi_window=14)

            # 이동평균과 RSI를 융합한 전략 계산
            signals_ma_rsi = signals_ma_rsi_strategy.generate_signals()

            # 그래프 그리기
            signals_ma_rsi_strategy.plot_moving_average_rsi_strategy(stock_data, signals_ma_rsi, self.ticker_company_dict[ticker], pdf_v4)
            # 선택된 ticker 출력
            print(f"{self.ticker_company_dict[ticker]} 주식 데이터의 Ticker: {ticker}")
        pdf_v4.close()
        pdf_v3.close()
        pdf_v2.close()
        pdf.close()

        # PDF 파일 닫기
