import logging
from pathlib import Path
from typing import Generator, List, Type, Union

from attr import define, field
from shutterbug.data.interfaces.external import InputInterface, FileLoaderInterface
from shutterbug.data.files.csv.loader import CSVLoader

_TYPES: List[Type[FileLoaderInterface]] = [CSVLoader]


@define
class FileInput(InputInterface):
    _input_files: List[Path] = field(init=False)

    @classmethod
    def from_path(cls, path: Path):
        """Creates a FileInput object from a singular path instead of a list of paths

        Parameters
        ----------
        cls : FileInput
            FileInput type
        path : Path
            Singular file or directory to find files from and attempt to load

        """

        return cls([path])

    def __init__(self, paths: List[Path]):
        self._input_files = self._get_files_from_paths(paths)

    def _get_files_from_path(self, path: Path) -> List[Path]:
        """Retreives all files from a given path, including from subdirectories

        Parameters
        ----------
        path : Path
            Path to iterate over

        Returns
        -------
        List[Path]
            All files in path, if any

        """
        result = []
        if path.is_dir():
            files = [x for x in path.iterdir() if x.is_file()]
            result.extend(files)
        elif path.is_file():
            result.append(path)
        return result

    def _get_files_from_paths(self, paths: List[Path]) -> List[Path]:
        """Iterates over all given paths and returns all files within those paths

        Parameters
        ----------
        paths : List[Path]
            Input paths, possibly directories

        Returns
        -------
        List[Path]
            All files in input paths

        """

        result = []
        for path in paths:
            result.extend(self._get_files_from_path(path))
        return result

    def _file_to_loader(self, path: Path) -> Union[None, FileLoaderInterface]:
        """Takes a given file and if it's readable by one of the loaders, return a readied loader of that type

        Parameters
        ----------
        path : Path
            File to load

        Returns
        -------
        FileLoaderInterface | None
            Either a FileLoader if a loader can load the file, or None if
            nothing can load the file.

        """
        for loader_type in _TYPES:
            if loader_type.is_readable(path):
                try:
                    return loader_type(input_file=path)  # type: ignore
                except ValueError as e:
                    logging.debug(
                        f"Loader type {type(loader_type)} unable to load file {path.name} due to error {e}"
                    )
        return None

    def __len__(self) -> int:
        """Number of files able to be loaded"""
        return len(self._input_files)

    def __iter__(self) -> Generator[FileLoaderInterface, None, None]:
        for i_file in self._input_files:
            loader = self._file_to_loader(i_file)
            if loader is not None:
                yield loader
            else:
                logging.warning(f"Unable to load file {i_file.name}")
