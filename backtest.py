# Import required libraries
import os
import shutil
import time
import pyfiglet
import importlib


import backtrader as bt
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


from rich.console import Console
from rich.progress import Progress
from datetime import datetime


console = Console()

console.clear()

# Generate and display ASCII art title
title = pyfiglet.figlet_format("BACKTEST", font="slant")
width = shutil.get_terminal_size().columns

for line in title.splitlines():
    console.print(line.center(width),style="bold bright_cyan",markup=False)

time.sleep(2)



# Keep validating the symbol until it is accepted or the program exits.
while True:

    symbol = console.input("[bold white]Select an symbol: ").upper() 
    
    if not symbol:
        print("Invalid symbol.")
        print("Please try again")
        continue

    try:
        ticker = yf.Ticker(symbol)

        # Confirm that the symbol exists and is valid.
        data = ticker.history(
            period="5d",
            interval="1d"
        )

        if data.empty:
            print(f"Invalid symbol '{symbol}'.")
            print("Please try again")
            continue

        print(f"Instrument verified: {symbol}")
        break

    except Exception:
        print(f"Could not verify '{symbol}'.")
        exit()
        print("Please try again")
        continue
    
# Timeframe
print()
print("Timeframe")
print("1. 1m   2. 5m   3. 15m   4. 1h   5. 1d")

timeframe_choice = int(input("Choose [1-5]: ") or "5")

timeframes = {
    1: "1m",
    2: "5m",
    3: "15m",
    4: "1h",
    5: "1d"
}

timeframe = timeframes.get(timeframe_choice)

# Dates
print()
start_date = input("Start date (YYYY-MM-DD) [Enter = all available]: ")
end_date = input("End date (YYYY-MM-DD) [Enter = latest]: ")

# STRATEGY SELECTION
print()
strategy_folder = "strategies"

strategies = [
    file[:-3]
    for file in os.listdir(strategy_folder)
    if file.endswith(".py") and file != "__init__.py"
]

print("Strategy")

for number, strategy in enumerate(strategies, start=1):
    print(f"{number}. {strategy}")

strategy_choice = input(f"Choose strategy [1-{len(strategies)}]: ") or "1"

while not strategy_choice.isdigit() or not (
    1 <= int(strategy_choice) <= len(strategies)
):
    print()
    print("Invalid strategy.")

    strategy_choice = input(f"Choose strategy [1-{len(strategies)}]: ") or "1"

strategy = strategies[int(strategy_choice) - 1]

print()
print(f"Strategy selected: {strategy}")

# Starting Capital
print()
starting_capital = float(input("Starting capital [$10,000]: ") or "10000")

# Risk Per Trade
print()
while True:
    try:
        risk_per_trade_fraction = float(
            input("Risk per trade [1%]: ") or "1"
        )

        if risk_per_trade_fraction > 0:
            risk_per_trade_fraction /= 100
            break
        
        print()
        print("Invalid input. Enter a number greater than 0.")

    except ValueError:
        print()
        print("Invalid input. Enter a number.")

# Risk-to-Reward
print()
while True:
    try:
        risk_reward_ratio = float(
            input("Risk-to-reward [1:2]: ").split(":")[-1] or "2"
        )

        if risk_reward_ratio > 0:
            break

        print("Invalid input. Enter a number greater than 0.")

    except ValueError:
        print("Invalid input. Example: 1:2")

# Slippage
print()
slippage = float(input("Slippage [0]: ") or "0")

# Commission
print()
commission_fraction = float(input("Commission [%0]: ") or "0") / 100

# Show Chart
print()
show_chart = input("Show chart? [Y/N]: ").upper() or "Y"

# Save Results
print()
save_results = input("Save results? [Y/N]: ").upper() or "N"

print()
print("========== BACKTEST SUMMARY ==========")

print(f"Symbol:              {symbol}")
print(f"Timeframe:           {timeframe}")
print(f"Start Date:          {start_date or 'All available'}")
print(f"End Date:            {end_date or 'Latest'}")
print(f"Strategy:            {strategy}")
print(f"Starting Capital:    ${starting_capital:,.2f}")
print(f"Risk Per Trade:      {risk_per_trade_fraction * 100:.2f}%")
print(f"Risk-to-Reward:      1:{risk_reward_ratio}")
print(f"Slippage:            {slippage}")
print(f"Commission:          {commission_fraction * 100:.2f}%")
print(f"Show Chart:          {'Yes' if show_chart else 'No'}")
print(f"Save Results:        {'Yes' if save_results else 'No'}")

print("======================================")

confirm = input("continue [Y/N]: ").upper() or "Y"

if confirm != "Y":
    print("Backtest cancelled.")
    exit()

#MARKET DATA
print()
print("Data Source")
print("1. Yahoo Finance")

print()
data_source = input("Choose [1]: ") or "1"

while data_source != "1":
    print()
    print("Invalid choice.")
    data_source = input("Choose [1]: ") or "1"

print("========== MARKET DATA ==========")

print(f"Symbol:    {symbol}")
print(f"Timeframe: {timeframe}")
print(f"Start:     {start_date or 'All available'}")
print(f"End:       {end_date or 'Latest'}")

download = input("Download market data? [Y/N]: ").upper() or "Y"

with Progress() as progress:

    print()
    task = progress.add_task(
        "[cyan]Downloading market data...",
        total=100
    )

    data = yf.download(
        symbol,
        start=start_date or None,
        end=end_date or None,
        interval=timeframe,
        auto_adjust=False,
        progress=False
    )

    # formatting data 
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Make column names standard for Backtrader
    data.columns = [column.lower() for column in data.columns]

    progress.update(task, completed=100)

os.makedirs("data", exist_ok=True)

file_path = f"data/{symbol}_{timeframe}.csv"

data.to_csv(file_path)

print()
print("Market data saved")
print()

confirm = input("Start backtest? [Y/N]: ").upper() or "Y"
print()

# Backtesting engine

cerebro = bt.Cerebro()

data_feed = bt.feeds.PandasData(dataname=data)

cerebro.adddata(data_feed)

strategy_module = importlib.import_module(f"strategies.{strategy}")

strategy_class = next(
    obj
    for obj in vars(strategy_module).values()
    if isinstance(obj, type)
    and issubclass(obj, bt.Strategy)
    and obj is not bt.Strategy
)

cerebro.addstrategy(strategy_class)

cerebro.broker.setcash(starting_capital)

class PortfolioValueAnalyzer(bt.Analyzer):

    def start(self):
        self.values = []
        self.dates = []

    def next(self):
        self.values.append(self.strategy.broker.getvalue())
        self.dates.append(self.strategy.datetime.datetime(0))

    def stop(self):
        self.rets['highest_value'] = max(self.values)
        self.rets['lowest_value'] = min(self.values)
        self.rets['values'] = self.values
        self.rets['dates'] = self.dates

cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
cerebro.addanalyzer(PortfolioValueAnalyzer, _name="portfolio")

results = cerebro.run()

ending_value = cerebro.broker.getvalue()

trade_analysis = results[0].analyzers.trades.get_analysis()

number_of_trades = trade_analysis.total.closed

winning_trades = trade_analysis.won.total
losing_trades = trade_analysis.lost.total

win_rate = (winning_trades / number_of_trades) * 100

gross_profit = trade_analysis.won.pnl.total
gross_loss = trade_analysis.lost.pnl.total

average_winning_trade = trade_analysis.won.pnl.average
average_losing_trade = trade_analysis.lost.pnl.average

profit_factor = gross_profit / abs(gross_loss)

total_net_profit = trade_analysis.pnl.net.total

average_profit_loss = trade_analysis.pnl.net.average

drawdown_analysis = results[0].analyzers.drawdown.get_analysis()
maximum_drawdown = drawdown_analysis.max.drawdown

average_trade_duration = trade_analysis.len.average

start = data.index.min()
end = data.index.max()

days = (end - start).days
weeks = days / 7

trade_frequency = number_of_trades / weeks

portfolio_analysis = results[0].analyzers.portfolio.get_analysis()

highest_value = portfolio_analysis['highest_value']
lowest_value = portfolio_analysis['lowest_value']

equity_values = portfolio_analysis['values']
equity_dates = portfolio_analysis['dates']

roi = ((ending_value - starting_capital) / starting_capital) * 100


print()
print("=" * 60)
print("                 ASTRA BACKTEST RESULTS")
print("=" * 60)

print()
print("PERFORMANCE")
print("-" * 60)
print(f"{'Number of Trades':<30} {number_of_trades:>15}")
print(f"{'Winning Trades':<30} {winning_trades:>15}")
print(f"{'Losing Trades':<30} {losing_trades:>15}")
print(f"{'Win Rate':<30} {win_rate:>14.2f}%")

print()
print("PROFITABILITY")
print("-" * 60)
print(f"{'Gross Profit':<30} {gross_profit:>15.2f}")
print(f"{'Gross Loss':<30} {gross_loss:>15.2f}")
print(f"{'Profit Factor':<30} {profit_factor:>15.2f}")
print(f"{'Total Net Profit':<30} {total_net_profit:>15.2f}")
print(f"{'Average Profit/Loss':<30} {average_profit_loss:>15.2f}")
print(f"{'ROI':<30} {roi:>14.2f}%")

print()
print("TRADE ANALYSIS")
print("-" * 60)
print(f"{'Average Winning Trade':<30} {average_winning_trade:>15.2f}")
print(f"{'Average Losing Trade':<30} {average_losing_trade:>15.2f}")
print(f"{'Average Trade Duration':<30} {average_trade_duration:>12.2f} bars")
print(f"{'Trade Frequency':<30} {trade_frequency:>10.2f} trades/week")

print()
print("ACCOUNT PERFORMANCE")
print("-" * 60)
print(f"{'Starting Capital':<30} {starting_capital:>15.2f}")
print(f"{'Highest Account Value':<30} {highest_value:>15.2f}")
print(f"{'Lowest Account Value':<30} {lowest_value:>15.2f}")
print(f"{'Maximum Drawdown':<30} {maximum_drawdown:>14.2f}%")
print(f"{'Ending Account Value':<30} {ending_value:>15.2f}")

print()
print("=" * 60)
print("                   BACKTEST COMPLETE")
print("=" * 60)
print()

# Save results

if save_results == "Y":

    os.makedirs("results", exist_ok=True)

    result_file = f"results/{symbol}_{timeframe}_results.txt"

    with open(result_file, "w") as file:

        file.write("=" * 60 + "\n")
        file.write("                 ASTRA BACKTEST RESULTS\n")
        file.write("=" * 60 + "\n\n")

        file.write("PERFORMANCE\n")
        file.write("-" * 60 + "\n")
        file.write(f"{'Number of Trades':<30} {number_of_trades:>15}\n")
        file.write(f"{'Winning Trades':<30} {winning_trades:>15}\n")
        file.write(f"{'Losing Trades':<30} {losing_trades:>15}\n")
        file.write(f"{'Win Rate':<30} {win_rate:>14.2f}%\n\n")

        file.write("PROFITABILITY\n")
        file.write("-" * 60 + "\n")
        file.write(f"{'Gross Profit':<30} {gross_profit:>15.2f}\n")
        file.write(f"{'Gross Loss':<30} {gross_loss:>15.2f}\n")
        file.write(f"{'Profit Factor':<30} {profit_factor:>15.2f}\n")
        file.write(f"{'Total Net Profit':<30} {total_net_profit:>15.2f}\n")
        file.write(f"{'Average Profit/Loss':<30} {average_profit_loss:>15.2f}\n")
        file.write(f"{'ROI':<30} {roi:>14.2f}%\n\n")

        file.write("TRADE ANALYSIS\n")
        file.write("-" * 60 + "\n")
        file.write(f"{'Average Winning Trade':<30} {average_winning_trade:>15.2f}\n")
        file.write(f"{'Average Losing Trade':<30} {average_losing_trade:>15.2f}\n")
        file.write(f"{'Average Trade Duration':<30} {average_trade_duration:>12.2f} bars\n")
        file.write(f"{'Trade Frequency':<30} {trade_frequency:>10.2f} trades/week\n\n")

        file.write("ACCOUNT PERFORMANCE\n")
        file.write("-" * 60 + "\n")
        file.write(f"{'Starting Capital':<30} {starting_capital:>15.2f}\n")
        file.write(f"{'Highest Account Value':<30} {highest_value:>15.2f}\n")
        file.write(f"{'Lowest Account Value':<30} {lowest_value:>15.2f}\n")
        file.write(f"{'Maximum Drawdown':<30} {maximum_drawdown:>14.2f}%\n")
        file.write(f"{'Ending Account Value':<30} {ending_value:>15.2f}\n")
        file.write(f"{'ROI':<30} {roi:>14.2f}%\n")

        file.write("\n")
        file.write("=" * 60 + "\n")
        file.write("                   BACKTEST COMPLETE\n")
        file.write("=" * 60 + "\n")

     
        equity_data = pd.DataFrame({
        "Date": equity_dates,
        "Account Value": equity_values})

        equity_file = f"results/{symbol}_{timeframe}_equity.csv"

        equity_data.to_csv(equity_file, index=False)


        print(f"Equity data saved to: {equity_file}")
        print()

        print("RESULTS SAVED")

        print()

        print(f"File: {result_file}")

print()

if show_chart == "Y":

    # Load equity data
    equity_data = pd.read_csv(f"results/{symbol}_{timeframe}_equity.csv") #dont hard code the file name, use the symbol and timeframe variables instead

    # Convert dates to datetime
    equity_data["Date"] = pd.to_datetime(equity_data["Date"])

    # Create equity curve
    plt.figure(figsize=(12, 6))

    plt.plot(
    equity_data["Date"],
    equity_data["Account Value"]
    )

    plt.title("ASTRA - Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Account Value")

    plt.grid(True)
    plt.tight_layout()

    print("Displaying equity curve chart...")
    time.sleep(1)

    plt.show()