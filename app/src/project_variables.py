from dotenv import load_dotenv
import os

load_dotenv()  # Load the env variables from .env for use

QUERY_URL = f"https://data.usajobs.gov/api/Search?"
LIMIT_RESULTS_PER_PAGE = "30"
LOCATION_NAME = "Chicago, Illinois"
JOB_POSITION_KEYWORD = "Data Engineering"
DB_TABLE = "jobs"
DB_VIEW = "chicago_jobs"
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")
OUTPUT_PATH="output.csv"
