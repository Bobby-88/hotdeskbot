from dotenv import load_dotenv
import os
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TG_TOKEN = os.getenv("TG_TOKEN")
Q_TG_TOKEN = os.getenv("Q_TG_TOKEN")
BT_TG_TOKEN = os.getenv("BT_TG_TOKEN")
EMAIL_PWD = os.getenv("EMAIL_PWD")
