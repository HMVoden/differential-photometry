from pathlib import Path
from typing import Dict
import xarray as xr
from shutterbug.file_loader.frame_loader.frame_interface import FrameLoaderInterface


class XarrayNetCDFLoader(FrameLoaderInterface):
    def load(path: Path, **settings: Dict) -> xr.Dataset:
        return xr.open_dataset(filename_or_obj=path, **settings)
