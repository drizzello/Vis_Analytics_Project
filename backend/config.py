from pathlib import Path

# 🔹 Base directory per i file
DATA_DIR = Path(__file__).resolve().parent / "data"

# 🔹 Definizione sorgenti
FILES = {
    "dwell_dynamic": DATA_DIR / "dwell_dynamic.parquet",
    "vessels": DATA_DIR / "vessels.parquet",
    #"fish": DATA_DIR / "fish.parquet",
    #"fish_locations": DATA_DIR / "fish_locations.parquet",
    "transactions": DATA_DIR / "transactions.parquet"
}
