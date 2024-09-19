import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


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
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
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