# Loads design/bed_params.json (Fusion Scripts may run with cwd elsewhere).
import json
import os


def load_bed_params():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, "..", "bed_params.json"))
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
