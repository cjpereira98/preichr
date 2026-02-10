import sys

# Add the MVC directories to the sys.path
from config.config import (
    FC,
    MODEL_DIR,
    VIEW_DIR,
    CONTROLLER_DIR,
    IMG_DIR,
    CSS_DIR,
    JS_DIR,
    BASE_DIR,
    UTILS_DIR,
)

sys.path.append(f"{BASE_DIR}")
sys.path.append(f"{UTILS_DIR}")
sys.path.append(f"{MODEL_DIR}")
sys.path.append(f"{VIEW_DIR}")
sys.path.append(f"{CONTROLLER_DIR}")

# Make variables available for import
__all__ = [
    "FC",
    "MODEL_DIR",
    "VIEW_DIR",
    "CONTROLLER_DIR",
    "IMG_DIR",
    "CSS_DIR",
    "JS_DIR",
    "BASE_DIR",
    "UTILS_DIR",
]