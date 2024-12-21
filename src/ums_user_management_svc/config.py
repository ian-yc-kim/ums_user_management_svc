import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DOMAIN_URL = os.getenv('DOMAIN_URL')

class Database:
    url = os.getenv('DATABASE_URL')