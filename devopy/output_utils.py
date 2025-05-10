import os
from datetime import datetime

def get_output_dir():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'devopy_outputs'))
    os.makedirs(out_dir, exist_ok=True)
    return out_dir

def unique_filename(prefix="wykres", ext="png"):
    dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}_{dt}.{ext}"
