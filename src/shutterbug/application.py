import logging
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from shutterbug.config import ApplicationConfig
from shutterbug.data import Dataset, DBReader, DBWriter
from shutterbug.data.file import FileInput
from shutterbug.data.interfaces.external import Input
from shutterbug.data.interfaces.internal import Reader, Writer
from shutterbug.init import (initialize_configuration, initialize_database,
                             initialize_logging)


def initialize_application(
    config_file: Optional[Path] = None,
    debug: bool = False,
) -> Tuple[ApplicationConfig, Engine]:
    initialize_logging(debug=debug)
    logging.info("Initializing application")
    config = initialize_configuration(config_file)
    db_path = config.data["database_path"]
    db_url = config.data["database_url"]
    database = initialize_database(db_path, db_url)
    logging.info("Finished initializing application")
    return config, database


def make_file_loader(path: Path) -> Input:
    return FileInput(path)


def make_reader_writer(
    path: Path, dataset_name: str, magnitude_limit: int, distance_limit: int
) -> Tuple[Reader, Writer]:
    engine = create_engine(url=path)
    reader = DBReader(
        dataset=dataset_name,
        engine=engine,
        mag_limit=magnitude_limit,
        distance_limit=distance_limit,
    )
    writer = DBWriter(dataset=dataset_name, engine=engine)
    return reader, writer


def make_dataset(dataset_name: str, reader: Reader, writer: Writer) -> Dataset:
    return Dataset(dataset_name, reader, writer)
