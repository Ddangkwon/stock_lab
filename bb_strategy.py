import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

class BollingerBandsStrategy:
    def __init__(self, data, window, num_std):
        self.data = data
        self.window = window
        self.num_std = num_std

    def calculate_bollinger_bands(self):
        rolling_mean = self.data['Close'].rolling(window=self.window).mean()
        rolling_std = self.data['Close'].rolling(window=self.window).std()
        upper_band = rolling_mean + (self.num_std * rolling_std)
        lower_band = rolling_mean - (self.num_std * rolling_std)
        return upper_band, lower_band

    def generate_signals(self):
        upper_band, lower_band = self.calculate_bollinger_bands()

        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0.0

        # Crossing upper band - Sell Signal
        signals['signal'][self.data['Close'] > upper_band] = -1.0

        # Crossing lower band - Buy Signal
        signals['signal'][self.data['Close'] < lower_band] = 1.0

        # Position change signal
        signals['positions'] = signals['signal'].diff()

        return signals

    def plot_bollinger_bands_strategy(self, stock_data, signals, company_name, pdf):
        upper_band, lower_band = self.calculate_bollinger_bands()

        plt.figure(figsize=(12, 6))
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        plt.plot(stock_data['Close'], label='Close Price')
        plt.plot(upper_band, label='Upper Bollinger Band', color='red')
        plt.plot(lower_band, label='Lower Bollinger Band', color='blue')
        plt.plot(signals.loc[signals.positions == 1.0].index,
                 stock_data['Close'][signals.positions == 1.0],
                 '^', markersize=10, color='g', lw=0, label='Buy Signal')
        plt.plot(signals.loc[signals.positions == -1.0].index,
                 stock_data['Close'][signals.positions == -1.0],
                 'v', markersize=10, color='r', lw=0, label='Sell Signal')
        plt.title(f'Bollinger Bands Strategy - {company_name}')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        pdf.savefig()
        plt.close()
