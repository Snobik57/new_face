import os
import sys
from face_compare.models.ch_db import DataBaseChORM

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
