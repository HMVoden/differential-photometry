from pathlib import Path
from typing import Optional, Protocol, Tuple

from sqlalchemy.engine import Engine
from shutterbug.config.application import ApplicationConfig
from shutterbug.data.interfaces.internal import DataReaderInterface, DataWriterInterface
import pandas as pd


class Initializer(Protocol):
    def initialize_logging(self, config_file: Path, debug: bool = False) -> None:
        ...

    def initialize_configuration(
        self,
        config_file: Optional[Path] = None,
    ) -> ApplicationConfig:
        ...

    def initialize_database(self, db_path: Path, db_url: str) -> Engine:
        ...

    def initialize_application(
        self, config_file: Optional[Path] = None, debug: bool = False
    ) -> Tuple[ApplicationConfig, Engine]:
        ...


class ConfigurationFactory(Protocol):
    def from_file(self, file: Path) -> ApplicationConfig:
        ...

    def to_file(self, file: Path, config: ApplicationConfig) -> bool:
        ...

    def data_folder(self) -> Path:
        ...


class DataFactory(Protocol):
    def load_file(
        self, file: Path, into: str
    ) -> Tuple[DataReaderInterface, DataWriterInterface]:
        ...

    def open_dataset(self, str) -> Tuple[DataReaderInterface, DataWriterInterface]:
        ...

    def write_file(self, file_path: Path, df: pd.DataFrame) -> None:
        ...


class Photometer(Protocol):
    def average_differential(
        self,
        target: pd.DataFrame,
        reference: pd.DataFrame,
        data_column: str,
        error_column: Optional[str] = None,
    ) -> pd.DataFrame:
        ...


class Grapher(Protocol):
    def graph(self, target: pd.DataFrame) -> None:
        ...
