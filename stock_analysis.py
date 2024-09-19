import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import mplfinance as mpf
import warnings
from ma_rsi_strategy import *
warnings.filterwarnings('ignore')


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
        # 매수 신호
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 stock_data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        # 매도 신호
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

        # 데이터 플롯
        fig, ax = mpf.plot(stock_data, type='candle', addplot=[ap_upper, ap_lower, ap_short_mavg, ap_long_mavg],
                           title=f'Moving Average Crossover Strategy - {company_name}', volume=False, style='charles',
                           warn_too_much_data=1000000, returnfig=True)
        # PDF에 저장
        pdf.savefig(fig)

    # 1. MACD 전략
    def calculate_macd(self, data, short_window=12, long_window=26, signal_window=9):
        data['EMA_short'] = data['Close'].ewm(span=short_window, adjust=False).mean()
        data['EMA_long'] = data['Close'].ewm(span=long_window, adjust=False).mean()
        data['MACD'] = data['EMA_short'] - data['EMA_long']
        data['Signal_line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
        return data

    def macd_strategy(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['MACD'] = data['MACD']
        signals['Signal_line'] = data['Signal_line']
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['MACD'] > signals['Signal_line'], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_macd_strategy(self, data, signals, company_name, pdf):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.title(f'MACD Strategy - {company_name}')
        plt.plot(data['Close'], label='Close Price')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.legend()
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(signals['MACD'], label='MACD', color='blue')
        plt.plot(signals['Signal_line'], label='Signal Line', color='red')
        plt.legend()
        plt.grid(True)

        pdf.savefig()
        plt.close()

    # 2. 스토캐스틱 오실레이터 전략
    def calculate_stochastic_oscillator(self, data, window=14, smooth_window=3):
        data['Lowest_Low'] = data['Low'].rolling(window=window).min()
        data['Highest_High'] = data['High'].rolling(window=window).max()
        data['%K'] = 100 * ((data['Close'] - data['Lowest_Low']) / (data['Highest_High'] - data['Lowest_Low']))
        data['%D'] = data['%K'].rolling(window=smooth_window).mean()
        return data

    def stochastic_oscillator_strategy(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['%K'] = data['%K']
        signals['%D'] = data['%D']
        signals['signal'] = 0.0
        signals['signal'] = np.where((signals['%K'] > signals['%D']) & (signals['%K'] < 20), 1.0, 0.0)
        signals['signal'] = np.where((signals['%K'] < signals['%D']) & (signals['%K'] > 80), -1.0, signals['signal'])
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_stochastic_oscillator_strategy(self, data, signals, company_name, pdf):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.title(f'Stochastic Oscillator Strategy - {company_name}')
        plt.plot(data['Close'], label='Close Price')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.legend()
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(signals['%K'], label='%K', color='blue')
        plt.plot(signals['%D'], label='%D', color='red')
        plt.axhline(20, color='gray', linestyle='--')
        plt.axhline(80, color='gray', linestyle='--')
        plt.legend()
        plt.grid(True)

        pdf.savefig()
        plt.close()

    # 3. 볼륨 가중 이동 평균(VWMA) 전략
    def calculate_vwma(self, data, window=20):
        price_volume = data['Close'] * data['Volume']
        vwma = price_volume.rolling(window=window).sum() / data['Volume'].rolling(window=window).sum()
        data['VWMA'] = vwma
        return data

    def vwma_strategy(self, data):
        data['SMA'] = data['Close'].rolling(window=20).mean()
        signals = pd.DataFrame(index=data.index)
        signals['VWMA'] = data['VWMA']
        signals['SMA'] = data['SMA']
        signals['signal'] = 0.0
        signals['signal'] = np.where(signals['VWMA'] > signals['SMA'], 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_vwma_strategy(self, data, signals, company_name, pdf):
        plt.figure(figsize=(12, 6))
        plt.title(f'VWMA Strategy - {company_name}')
        plt.plot(data['Close'], label='Close Price')
        plt.plot(data['VWMA'], label='VWMA', color='orange')
        plt.plot(data['SMA'], label='SMA', color='purple')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()

    # 4. 일목균형표(Ichimoku Cloud) 전략
    def calculate_ichimoku_cloud(self, data):
        high9 = data['High'].rolling(window=9).max()
        low9 = data['Low'].rolling(window=9).min()
        data['Conversion_Line'] = (high9 + low9) / 2

        high26 = data['High'].rolling(window=26).max()
        low26 = data['Low'].rolling(window=26).min()
        data['Base_Line'] = (high26 + low26) / 2

        data['Leading_Span_A'] = ((data['Conversion_Line'] + data['Base_Line']) / 2).shift(26)
        high52 = data['High'].rolling(window=52).max()
        low52 = data['Low'].rolling(window=52).min()
        data['Leading_Span_B'] = ((high52 + low52) / 2).shift(26)
        data['Lagging_Span'] = data['Close'].shift(-26)
        return data

    def ichimoku_strategy(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['Conversion_Line'] = data['Conversion_Line']
        signals['Base_Line'] = data['Base_Line']
        signals['Leading_Span_A'] = data['Leading_Span_A']
        signals['Leading_Span_B'] = data['Leading_Span_B']
        signals['signal'] = 0.0
        signals['signal'] = np.where((data['Conversion_Line'] > data['Base_Line']) &
                                     (data['Close'] > data['Leading_Span_A']) &
                                     (data['Close'] > data['Leading_Span_B']), 1.0, 0.0)
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_ichimoku_strategy(self, data, signals, company_name, pdf):
        plt.figure(figsize=(12, 6))
        plt.title(f'Ichimoku Cloud Strategy - {company_name}')
        plt.plot(data['Close'], label='Close Price')
        plt.plot(data['Conversion_Line'], label='Conversion Line', color='blue')
        plt.plot(data['Base_Line'], label='Base Line', color='red')
        plt.fill_between(data.index, data['Leading_Span_A'], data['Leading_Span_B'],
                         where=data['Leading_Span_A'] >= data['Leading_Span_B'],
                         facecolor='green', alpha=0.3)
        plt.fill_between(data.index, data['Leading_Span_A'], data['Leading_Span_B'],
                         where=data['Leading_Span_A'] < data['Leading_Span_B'],
                         facecolor='red', alpha=0.3)
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()

    # 5. 평균 방향성 지수(ADX) 전략
    def calculate_adx(self, data, window=14):
        delta_high = data['High'].diff()
        delta_low = data['Low'].diff()
        plus_dm = np.where((delta_high > delta_low) & (delta_high > 0), delta_high, 0.0)
        minus_dm = np.where((delta_low > delta_high) & (delta_low > 0), delta_low, 0.0)
        tr1 = data['High'] - data['Low']
        tr2 = abs(data['High'] - data['Close'].shift())
        tr3 = abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=window).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=window).mean() / atr)
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(window=window).mean()
        data['ADX'] = adx
        data['Plus_DI'] = plus_di
        data['Minus_DI'] = minus_di
        return data

    def adx_strategy(self, data):
        signals = pd.DataFrame(index=data.index)
        signals['ADX'] = data['ADX']
        signals['Plus_DI'] = data['Plus_DI']
        signals['Minus_DI'] = data['Minus_DI']
        signals['signal'] = 0.0
        signals['signal'] = np.where((signals['Plus_DI'] > signals['Minus_DI']) & (signals['ADX'] > 25), 1.0, 0.0)
        signals['signal'] = np.where((signals['Plus_DI'] < signals['Minus_DI']) & (signals['ADX'] > 25), -1.0, signals['signal'])
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_adx_strategy(self, data, signals, company_name, pdf):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.title(f'ADX Strategy - {company_name}')
        plt.plot(data['Close'], label='Close Price')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.legend()
        plt.grid(True)

        plt.subplot(2, 1, 2)
        plt.plot(signals['ADX'], label='ADX', color='orange')
        plt.axhline(25, color='gray', linestyle='--')
        plt.legend()
        plt.grid(True)

        pdf.savefig()
        plt.close()

    # 전체 주식 분석 실행
    def analyze_stocks(self):
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = '2020-01-01'
        end_date = current_date

        # 기존 PDF 파일들
        pdf_path = 'result/stock_analysis.pdf'
        pdf = PdfPages(pdf_path)
        pdf_path_v2 = 'result/stock_analysis_v2.pdf'
        pdf_v2 = PdfPages(pdf_path_v2)
        pdf_path_v3 = 'result/stock_analysis_v3.pdf'
        pdf_v3 = PdfPages(pdf_path_v3)
        pdf_path_v4 = 'result/stock_analysis_v4.pdf'
        pdf_v4 = PdfPages(pdf_path_v4)

        # 새로운 전략을 위한 PDF 파일
        pdf_path_macd = 'result/stock_analysis_macd.pdf'
        pdf_macd = PdfPages(pdf_path_macd)
        pdf_path_stochastic = 'result/stock_analysis_stochastic.pdf'
        pdf_stochastic = PdfPages(pdf_path_stochastic)
        pdf_path_vwma = 'result/stock_analysis_vwma.pdf'
        pdf_vwma = PdfPages(pdf_path_vwma)
        pdf_path_ichimoku = 'result/stock_analysis_ichimoku.pdf'
        pdf_ichimoku = PdfPages(pdf_path_ichimoku)
        pdf_path_adx = 'result/stock_analysis_adx.pdf'
        pdf_adx = PdfPages(pdf_path_adx)

        for ticker in self.ticker_company_dict.keys():
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
            # mplfinance 패키지를 사용한 플롯
            self.plot_mplfinance(stock_data, signals, self.ticker_company_dict[ticker], upper_band, lower_band, pdf_v2, returns)

            # RSI 전략 계산 및 시각화
            signals_rsi = self.rsi_strategy(stock_data, window=14)
            self.plot_rsi_strategy(stock_data, signals_rsi, self.ticker_company_dict[ticker], pdf_v3)
            # MovingAverageRSIStrategy 클래스의 인스턴스 생성
            signals_ma_rsi_strategy = MovingAverageRSIStrategy(stock_data, short_window=50, long_window=200,
                                                               rsi_window=14)

            # 이동평균과 RSI를 융합한 전략 계산
            signals_ma_rsi = signals_ma_rsi_strategy.generate_signals()

            # 그래프 그리기
            signals_ma_rsi_strategy.plot_moving_average_rsi_strategy(stock_data, signals_ma_rsi, self.ticker_company_dict[ticker], pdf_v4)

            # MACD 전략 계산 및 시각화
            stock_data_macd = self.calculate_macd(stock_data)
            signals_macd = self.macd_strategy(stock_data_macd)
            self.plot_macd_strategy(stock_data_macd, signals_macd, self.ticker_company_dict[ticker], pdf_macd)

            # 스토캐스틱 오실레이터 전략 계산 및 시각화
            stock_data_stochastic = self.calculate_stochastic_oscillator(stock_data)
            signals_stochastic = self.stochastic_oscillator_strategy(stock_data_stochastic)
            self.plot_stochastic_oscillator_strategy(stock_data_stochastic, signals_stochastic, self.ticker_company_dict[ticker], pdf_stochastic)

            # VWMA 전략 계산 및 시각화
            stock_data_vwma = self.calculate_vwma(stock_data)
            signals_vwma = self.vwma_strategy(stock_data_vwma)
            self.plot_vwma_strategy(stock_data_vwma, signals_vwma, self.ticker_company_dict[ticker], pdf_vwma)

            # 일목균형표 전략 계산 및 시각화
            stock_data_ichimoku = self.calculate_ichimoku_cloud(stock_data)
            signals_ichimoku = self.ichimoku_strategy(stock_data_ichimoku)
            self.plot_ichimoku_strategy(stock_data_ichimoku, signals_ichimoku, self.ticker_company_dict[ticker], pdf_ichimoku)

            # ADX 전략 계산 및 시각화
            stock_data_adx = self.calculate_adx(stock_data)
            signals_adx = self.adx_strategy(stock_data_adx)
            self.plot_adx_strategy(stock_data_adx, signals_adx, self.ticker_company_dict[ticker], pdf_adx)

            # 선택된 ticker 출력
            print(f"{self.ticker_company_dict[ticker]} 주식 데이터의 Ticker: {ticker}")

        # PDF 파일 닫기
        pdf_adx.close()
        pdf_ichimoku.close()
        pdf_vwma.close()
        pdf_macd.close()
        pdf_stochastic.close()
        pdf_v4.close()
        pdf_v3.close()
        pdf_v2.close()
        pdf.close()
