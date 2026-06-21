import json

WATERMARK_FILE = "pipeline/state/watermark.json"


def load_watermark():
    with open(WATERMARK_FILE, "r") as f:
        return json.load(f)


def save_watermark(state):
    with open(WATERMARK_FILE, "w") as f:
        json.dump(state, f, indent=4)