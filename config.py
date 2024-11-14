import logging
import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

    LOGGING_LEVEL = logging.INFO
    LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_TO_FILE = False
    LOGGING_FILE = os.path.join(os.path.dirname(__file__), 'app.log')

    @classmethod
    def get_db_uri(cls, host: str, db_name: str) -> str:
        if not cls.POSTGRES_USER or not cls.POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_USER and POSTGRES_PASSWORD variables must be set.")
        return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{host}/{db_name}"

    @classmethod
    def init_logging(cls):
        handlers = [logging.StreamHandler()]
        if cls.LOG_TO_FILE:
            handlers.append(logging.FileHandler(cls.LOGGING_FILE))
        logging.basicConfig(level=cls.LOGGING_LEVEL,
                            format=cls.LOGGING_FORMAT,
                            handlers=handlers)

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = "localhost"
    DB_NAME = "library"
    ADMIN_EMAIL = "admin@example.com"
    try:
        SQLALCHEMY_DATABASE_URI = Config.get_db_uri(host=DB_HOST, db_name=DB_NAME)
    except ValueError as e:
        raise ValueError(f"Failed to configure database: {e}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    Config.init_logging()
