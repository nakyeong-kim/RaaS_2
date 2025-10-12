# backend/tools.py
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from io import StringIO, BytesIO

def _load_csv_or_text(data_str_or_path):
    """Accepts raw CSV text or a file path."""
    try:
        # if path exists, read file
        if os.path.exists(data_str_or_path):
            return pd.read_csv(data_str_or_path)
        # else try to parse as CSV content
        return pd.read_csv(StringIO(data_str_or_path))
    except Exception:
        # try excel
        try:
            return pd.read_excel(data_str_or_path)
        except Exception as e:
            raise ValueError(f"Cannot parse data: {e}")

def summarize_dataframe(data):
    """
    data: CSV content string or path to csv/xlsx
    returns: JSON string with basic stats (describe + top rows)
    """
    df = _load_csv_or_text(data)
    desc = df.describe(include='all').to_dict()
    head = df.head(5).to_dict(orient="records")
    out = {"describe": desc, "head": head, "shape": df.shape}
    return json.dumps(out, default=str, ensure_ascii=False)

def plot_dataframe(data, x, y, kind="line", out_dir="storage/plots"):
    """
    data: CSV content or path
    x, y: column names
    returns: path to saved image
    """
    os.makedirs(out_dir, exist_ok=True)
    df = _load_csv_or_text(data)
    if x not in df.columns or y not in df.columns:
        raise ValueError("x or y column not found in dataframe")
    plt.figure()
    if kind == "line":
        df.plot(x=x, y=y)
    elif kind == "bar":
        df.plot.bar(x=x, y=y)
    else:
        df.plot(x=x, y=y)
    out_path = os.path.join(out_dir, f"plot_{abs(hash((x,y)))%100000}.png")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    return out_path
