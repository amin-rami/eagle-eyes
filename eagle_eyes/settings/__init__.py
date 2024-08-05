import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

from .django import *  # noqa: F401, E402, F403  # All Django related settings
from .third_party import *  # noqa: F401, E402, F403  # Celery, Django REST Framework & other 3rd parties
from .project import *  # noqa: F401, E402, F403  # You custom settings
