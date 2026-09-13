# Import required libraries
import shutil
import time
import pyfiglet
from rich.console import Console
import subprocess
import sys

console = Console()

# Generate and display ASCII art title
title = pyfiglet.figlet_format("ASTRA", font="slant")
width = shutil.get_terminal_size().columns

for line in title.splitlines():
    console.print(line.center(width),style="bold bright_cyan",markup=False)

time.sleep(2)

# Define menu options
menu_options = [
    "Exit",
    "Start Backtest",
    "Strategy",
    "View Results",
    "Load Historical Data",
    "Settings",
    "Diagnostics",
]

# Display menu title and options
console.print()
console.print("ASTRA MENU",style="bold white")
console.print()

for number, option in enumerate(menu_options, start=0):
    menu_item = f"[{number}] {option}"
    console.print(menu_item,style="bright_cyan")

# Prompt user for selection
console.print()
while True:
    choice = console.input("[bold white]Select an option: ")


    if choice == "1":
        subprocess.run([sys.executable, "start_backtest.py"])
        break

    elif choice == "2":
        subprocess.run([sys.executable, "strategy.py"])
        break

    elif choice == "3":
        subprocess.run([sys.executable, "view_results.py"])
        break

    elif choice == "4":
        subprocess.run([sys.executable, "load_data.py"])
        break

    elif choice == "5":
        subprocess.run([sys.executable, "settings.py"])
        break

    elif choice == "6":
        subprocess.run([sys.executable, "diagnostics.py"])
        break

    elif choice == "0":
        console.print("Exiting ASTRA...",style="bold bright_cyan")
        time.sleep(2)
        break

    else:
        console.print("\nInvalid option.",style="bold red")