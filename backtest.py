# Import required libraries
import os
import shutil
import time
import yfinance as yf
import pyfiglet
from rich.console import Console
from rich.progress import Progress

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

confirm = input("\nStart backtest? [Y/N]: ").upper() or "Y"

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

download = input("\nDownload market data? [Y/N]: ").upper() or "Y"

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

    progress.update(task, completed=100)

os.makedirs("data", exist_ok=True)

file_path = f"data/{symbol}_{timeframe}.csv"

data.to_csv(file_path)

print()
print(" Market data saved")