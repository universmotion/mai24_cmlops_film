from pathlib import Path
import sys
from unittest.mock import patch
import os

path = Path(__file__).parent.parent
sys.path.append(str(path))

# Add env
patch.dict(os.environ, {
    "SECRET_API": "secret_test",
    "DB_USER": "user",
    "DB_PASSWORD": "pass",
    "DB_HOST": "0.0.0.0",
    "DB_PORT": "8000",
    "DB_NAME": "db_name"
}).start()
