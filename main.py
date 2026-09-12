# Import required libraries
import shutil
import time
import pyfiglet
from rich.console import Console

console = Console()

# Generate and display ASCII art title
title = pyfiglet.figlet_format("ASTRA", font="slant")
width = shutil.get_terminal_size().columns

for line in title.splitlines():
    console.print(line.center(width),style="bold bright_cyan",markup=False)

time.sleep(2)

# Define menu options
menu_options = [
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

for number, option in enumerate(menu_options, start=1):
    menu_item = f"[{number}] {option}"
    console.print(menu_item,style="bright_cyan")

# Prompt user for selection
console.print()
console.print("Select an option: ", style="bold white")