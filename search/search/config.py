"""search485 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

SEARCH_ROOT = pathlib.Path(__file__).resolve().parent

# Database file is var/wikipedia.sqlite3
DATABASE_FILENAME = SEARCH_ROOT/'var'/'wikipedia.sqlite3'
INDEX_API_URL = "http://localhost:8001/api/v1/hits/"
