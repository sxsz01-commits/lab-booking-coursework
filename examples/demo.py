"""Seed and print sample labs without starting the server."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from my_tool.db import ROOT, init_db, list_labs

path = ROOT / "data" / "lab.db"
init_db(path)
for lab in list_labs(path):
    print(f"{lab['id']}: {lab['name']} ({lab['capacity']} 人) - {lab['location']}")

