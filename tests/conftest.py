import os
import sys

# Os modulos do bot importam uns aos outros a partir de src/ (ex.: "from database.database import ...")
SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC not in sys.path:
    sys.path.insert(0, SRC)
