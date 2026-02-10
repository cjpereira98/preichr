import sys
import os

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

os.system('..\\scripts\\turbo_ps\\turbo_ps.py') #how to call a script from in here