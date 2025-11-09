import pandas as pd
from functools import lru_cache
from .config import FILES

@lru_cache(maxsize=None)
def load_parquet(name: str) -> pd.DataFrame:
    """Carica un DataFrame parquet e lo mette in cache."""
    path = FILES.get(name)
    if not path or not path.exists():
        raise FileNotFoundError(f"File '{name}' non trovato in {path}")
    return pd.read_parquet(path)

# Shortcut specifici
def get_dwell_dynamic(): return load_parquet("dwell_dynamic")
def get_vessels(): return load_parquet("vessels")
def get_fish(): return load_parquet("fish")
def get_transactions(): return load_parquet("transactions")
def get_fish_locations(): return load_parquet("fish_locations")
def get_trans(): return load_parquet("trans")
def get_pings(): return load_parquet("pings")

