import os
import pathlib
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_TITLE: str = "NTerminal"
    PROJECT_VERSION: str = "0.1.1"
    DATA_PATH = os.getenv("DATA_PATH", pathlib.Path(os.getcwd(),"data"))
    PASSWORD_EXPIRATION: str = os.getenv("PASSWORD_EXPIRATION")

settings = Settings()
