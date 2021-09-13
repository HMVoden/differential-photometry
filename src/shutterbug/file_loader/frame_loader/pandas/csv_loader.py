from pathlib import Path
from typing import Dict
import pandas as pd
from shutterbug.file_loader.frame_loader.frame_interface import FrameLoaderInterface


class PandasCSVLoader(FrameLoaderInterface):
    def load(path: Path, **settings: Dict) -> pd.DataFrame:
        return pd.read_csv(reader=path, **settings)
