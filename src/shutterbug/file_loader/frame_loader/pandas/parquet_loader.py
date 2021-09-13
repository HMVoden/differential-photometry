from pathlib import Path
from typing import Dict
import pandas as pd
from shutterbug.file_loader.frame_loader.frame_interface import FrameLoaderInterface


class PandasParquetLoader(FrameLoaderInterface):
    def load(path: Path, **settings: Dict):
        return pd.read_parquet(path=path, **settings)
