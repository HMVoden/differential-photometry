import logging
from pathlib import Path
from typing import Generator, List, Tuple, Literal, Union
from attr import define

from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session
from attr import define, field
import shutterbug.differential as Differential
from shutterbug.analysis.feature import IQR, FeatureBase, InverseVonNeumann
from shutterbug.config import ApplicationConfig
from shutterbug.data import Dataset, DBReader, DBWriter
from shutterbug.data.file import FileInput
from shutterbug.data.graphing.builder import BuilderBase
from shutterbug.data.graphing.seaborn_builder import SeabornBuilder
from shutterbug.data.interfaces.external import Input
from shutterbug.data.interfaces.internal import Reader, Writer
from shutterbug.init import (
    initialize_configuration,
    initialize_database,
    initialize_logging,
)
from shutterbug.interfaces.internal import Photometer


@define
class Shutterbug:
    def load_file(
        self, file_path: Path, into: Literal["memory", "database"]
    ) -> List[str]:
        """Loads file into either memory or database for use, returns list of star names in dataset"""
        pass

    def graph_star(self, star: str, folder: Union[Path, None]) -> bool:
        """Outputs star to specified directory, or default directory if none given.
        Returns boolean on success or failure"""
        pass

    def calculate_differential_magnitude(
        self,
        star: str,
    ) -> bool:
        """Calculates differential magnitude on given star, using reference stars from dataset
        Returns boolean on success or failure"""
        pass

    def calculate_features(self, star: str) -> bool:
        """Calculates statistical features of given star based on configuration settings
        Returns boolean on success or failure"""
        pass

    def _load_configuration(self, path: Union[Path, None]) -> ApplicationConfig:
        """Loads the application's configuration from given path, or from default if none given
        Returns ApplicationConfig object"""
        pass

    def _initialize_logging(self, debug: bool) -> bool:
        """Initializes logging with optional debug logging,
        Returns boolean on success or failure"""
        pass


def initialize_application(
    config_file: Path = Path().cwd() / "shutterbug.ini",
    debug: bool = False,
) -> Tuple[ApplicationConfig, Engine]:
    initialize_logging(debug=debug)
    logging.info("Initializing application")
    config = initialize_configuration(config_file)
    db_path = config.data.database_path
    db_url = config.data.database_url
    database = initialize_database(db_path, db_url)
    logging.info("Finished initializing application")
    return config, database


def make_file_loader(path: Path) -> Input:
    return FileInput(path)


def make_reader_writer(
    dataset_name: str, magnitude_limit: int, distance_limit: int, engine: Engine
) -> Generator[Tuple[Reader, Writer], None, None]:
    with Session(engine) as session:
        reader = DBReader(
            dataset=dataset_name,
            session=session,
            mag_limit=magnitude_limit,
            distance_limit=distance_limit,
        )
        writer = DBWriter(dataset=dataset_name, session=session)
        yield reader, writer


def make_dataset(dataset_name: str, reader: Reader, writer: Writer) -> Dataset:
    return Dataset(dataset_name, reader, writer, store_in_memory=True)


def get_feature_calculators(config: ApplicationConfig) -> List[FeatureBase]:
    threshholds = config.variability

    return [
        InverseVonNeumann(threshhold=threshholds.ivn),
        IQR(threshhold=threshholds.iqr),
    ]


def get_photometer() -> Photometer:
    return Differential


def get_graph_builder() -> BuilderBase:
    return SeabornBuilder()


def make_folder(folder: Path):
    folder = Path(folder)  # sanity check
    folder.mkdir(exist_ok=True, parents=True)


def make_output_folder(dataset_name: str, output_folder: Path):
    make_folder(output_folder / dataset_name / "variable")
    make_folder(output_folder / dataset_name / "nonvariable")
    return output_folder / dataset_name
