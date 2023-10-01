import backtrader as bt
import numpy as np
from scipy.stats import linregress
import pandas as pd
from get_stocks import get_dir_stocks
import matplotlib.pyplot as plt

# Momentum Indicator
class Momentum(bt.Indicator):
    lines = ('trend',)
    params = (('period', 90),)
    
    def __init__(self):
        self.addminperiod(self.params.period)
    
    def next(self):
        returns = np.log(self.data.get(size=self.p.period))
        x = np.arange(len(returns))
        slope, _, rvalue, _, _ = linregress(x, returns)
        annualized = (1 + slope) ** 252
        self.lines.trend[0] = annualized * (rvalue ** 2)

# Momentum Strategy
class Strategy(bt.Strategy):
    def __init__(self):
        self.i = 0
        self.inds = {}
        self.spy = self.datas[0]
        self.stocks = self.datas[1:]
        self.portfolio_values = []
        
        self.spy_sma200 = bt.indicators.SimpleMovingAverage(self.spy.close, period=200)
        for d in self.stocks:
            self.inds[d] = {}
            self.inds[d]["momentum"] = Momentum(d.close, period=90)
            self.inds[d]["sma100"] = bt.indicators.SimpleMovingAverage(d.close, period=100)
            self.inds[d]["atr20"] = bt.indicators.ATR(d, period=20)

    def prenext(self):
        self.next()

    def next(self):
        if self.i % 5 == 0:
            self.rebalance_portfolio()
        
        if self.i % 10 == 0:
            self.rebalance_positions()
        
        self.i += 1
        self.portfolio_values.append(self.broker.get_value())

    def rebalance_portfolio(self):
        self.rankings = list(filter(lambda d: len(d) > 100, self.stocks))
        self.rankings.sort(key=lambda d: self.inds[d]["momentum"][0])
        num_stocks = len(self.rankings)
        
        for i, d in enumerate(self.rankings):
            if self.getposition(self.data).size:
                if i > num_stocks * 0.2 or d < self.inds[d]["sma100"]:
                    self.close(d)
        
        if self.spy < self.spy_sma200:
            return
        
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            if not self.getposition(self.data).size:
                size = value * 0.001 / self.inds[d]["atr20"]
                self.buy(d, size=size)

    def rebalance_positions(self):
        num_stocks = len(self.rankings)
        
        if self.spy < self.spy_sma200:
            return
        
        for i, d in enumerate(self.rankings[:int(num_stocks * 0.2)]):
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            if cash <= 0:
                break
            size = value * 0.001 / self.inds[d]["atr20"]
            self.order_target_size(d, size)
            
# Initialize Cerebro
cerebro = bt.Cerebro(stdstats=False)
cerebro.broker.set_coc(True)

# Add Data
tickers = get_dir_stocks('./IVV_Constitutents_Price_Data_Dec_2022')
datafeeds = [
    bt.feeds.PandasData(dataname=pd.read_csv(f'./IVV_Constitutents_Price_Data_Dec_2022/{ticker}.csv', parse_dates=True, index_col=0), plot=False, name=ticker)
    for ticker in tickers if len(pd.read_csv(f'./IVV_Constitutents_Price_Data_Dec_2022/{ticker}.csv')) > 100
]
for data in datafeeds:
    cerebro.adddata(data)

# Add Strategy, and Analyzer
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return')
cerebro.addstrategy(Strategy)

# Run the Backtest
results = cerebro.run()

daily_returns = list(results[0].analyzers.time_return.get_analysis().values())

portfolio_value = np.array(results[0].portfolio_values)
initial_portfolio_value = portfolio_value[0]

# Total Returns
total_return = (portfolio_value[-1] - initial_portfolio_value) / initial_portfolio_value * 100
print(f"Total Return: {total_return:.2f}%")

# Data span (in years)
start_date = pd.Timestamp('2022-03-01')
end_date = pd.Timestamp('2023-07-28')
years = (end_date - start_date).days / 365.25

# Annualized Returns
annualized_return = (portfolio_value[-1] / initial_portfolio_value) ** (1 / years) - 1
annualized_return *= 100
print(f"Annualized Return: {annualized_return:.2f}%")

# Max Drawdown
running_max = np.maximum.accumulate(portfolio_value)
running_drawdown = (portfolio_value - running_max) / running_max
max_drawdown = np.min(running_drawdown) * 100
print(f"Max Drawdown: {max_drawdown:.2f}%")

# Sharpe Ratio
daily_returns = np.diff(portfolio_value) / portfolio_value[:-1]
risk_free_rate = 0.01029
annualized_return_decimal = annualized_return / 100
sharpe_ratio = (annualized_return_decimal - risk_free_rate) / (daily_returns.std() * np.sqrt(252))
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# Extract data from the strategy
portfolio_values = np.array(results[0].portfolio_values)
dates = [bt.num2date(dt) for dt in results[0].datas[0].datetime.array]

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(dates, portfolio_values, label='Portfolio Value', color='salmon')
plt.title('Portfolio Value Over Time')
plt.xlabel('Date')
plt.ylabel('Portfolio Value in $')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()