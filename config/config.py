from dotenv import load_dotenv
from pathlib import Path
import os


ROOT_PATH = Path(os.path.dirname(__file__)) / '..'
SERVER_PATH = ROOT_PATH / 'server'
ENV_PATH = ROOT_PATH / '.env'
load_dotenv(dotenv_path=ENV_PATH)

DB_INFO = {
    'drivername': 'mysql+pymysql',
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS')
}

HOST = os.getenv('SERVER_HOST') or '0.0.0.0'
DEBUG = True if (os.getenv('DEBUG') if os.getenv('DEBUG') else "").lower() == 'true' else False
SECRET_KEY = os.getenv('KEY')