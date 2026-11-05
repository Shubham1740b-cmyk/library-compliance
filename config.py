"""Application-wide settings. Deliberately kept outside the three MVVM layers."""
import os

DATABASE = "library.db"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-locally")   # P1: secret code mein nahi
DEBUG = False                                                # P2: debug OFF
LOG_FILE = "logs/app.log"                                    # P3: alag log file

# --- Library identification -------------------------------------------------
LIBRARY_NAME = "shubhamkumar's Library"  # Updated for assignment requirement

# --- Library business policy ------------------------------------------------
LOAN_PERIOD_DAYS = 14      # how long a member may keep a book
MAX_BOOKS_PER_MEMBER = 3   # how many books one member may hold at once
FINE_PER_DAY = 5           # rupees charged for each day a book is late