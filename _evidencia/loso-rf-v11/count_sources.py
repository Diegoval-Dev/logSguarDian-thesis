import pandas as pd
from pathlib import Path
SPLITS = Path("/Users/diego/Uvg/Proyecto de Graduacion/logSguarDian/training/splits")
frames = [pd.read_parquet(SPLITS / name, columns=["_source"]) for name in ("train.parquet", "val.parquet")]
counts = pd.concat(frames, ignore_index=True)["_source"].value_counts()
for source, n in counts.items():
    print(f"{source}\t{n}")
print(f"TOTAL\t{int(counts.sum())}")
