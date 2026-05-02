import sys
import os
import platform
from typing import Any

colors: bool = True  # Output should be colored
machine: str = sys.platform  # Detecting the os of current system
checkplatform: str = platform.platform() # Get current version of OS
if machine.lower().startswith(('os', 'win', 'darwin', 'ios')):
    colors = False  # Colors shouldn't be displayed on mac & windows
if checkplatform.startswith("Windows-10") and int(platform.version().split(".")[2]) >= 10586:
    colors = True
    os.system('')   # Enables the ANSI
if not colors:
    end = red = white = green = yellow = run = bad = good = info = que = ''
else:
    white: str = '\033[97m'
    green: str = '\033[92m'
    red: str = '\033[91m'
    yellow: str = '\033[93m'
    end: str = '\033[0m'
    back: str = '\033[7;91m'
    info: str = '\033[93m[!]\033[0m'
    que: str = '\033[94m[?]\033[0m'
    bad: str = '\033[91m[-]\033[0m'
    good: str = '\033[92m[+]\033[0m'
    run: str = '\033[97m[~]\033[0m'
