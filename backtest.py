# Import required libraries
import shutil
import time
import yfinance as yf
import pyfiglet
from rich.console import Console

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
    