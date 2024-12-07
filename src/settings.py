import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv(".dbenvironment")
load_dotenv(".env")


@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv('TG_TOKEN_BOT')
    ABSPATH: str = os.path.abspath(__file__)
    DB_DRIVER_NAME = "postgresql+psycopg2"
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    PGHOST = os.getenv("PGHOST")
    PGPORT = os.getenv("PGPORT")


settings = Settings()