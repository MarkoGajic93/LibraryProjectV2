import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")

    @classmethod
    def get_db_uri(cls, host: str, db_name: str) -> str:
        if not cls.POSTGRES_USER or not cls.POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_USER and POSTGRES_PASSWORD variables must be set.")
        return f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}@{host}/{db_name}"

class DevelopmentConfig(Config):
    DEBUG = True
    DB_HOST = "localhost"
    DB_NAME = "library"
    ADMIN_EMAIL = "admin@example.com"
    try:
        DATABASE = Config.get_db_uri(host=DB_HOST, db_name=DB_NAME)
    except ValueError as e:
        raise ValueError(f"Failed to configure database: {e}")
