import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    url = os.getenv("DATABASE_URL")