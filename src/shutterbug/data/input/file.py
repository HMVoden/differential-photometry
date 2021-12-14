from pathlib import Path
from typing import Generator, Iterator, List, Mapping, Union

from attr import define, field
from shutterbug.data.core.interface.input import InputInterface
from shutterbug.data.core.interface.loader import FileLoaderInterface
from shutterbug.data.input.csv.header import check_headers
from shutterbug.data.input.csv.loader import CSVLoader


@define
class FileInput(InputInterface):
    _TYPES: List[FileLoaderInterface] = list((CSVLoader))
    _input_loaders: List[FileLoaderInterface] = field(init=False)

    @classmethod
    def from_path(cls, path: Path):
        """Creates a FileInput type from a singular path instead of a list of paths

        Parameters
        ----------
        cls : FileInput
            FileInput type
        path : Path
            Singular file or directory to find files from and attempt to load

        """

        cls([path])

    def __init__(self, paths: List[Path]):
        files_from_path = self._get_files_from_paths(paths)
        loaders = list(map(self._file_to_loader, files_from_path))
        if loaders is not None:
            self._input_loaders.extend(loaders)
        else:
            raise ValueError("Cannot read any input files")

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

        for loader_type in self._TYPES:
            if loader_type.is_readable(path):
                known_header = check_headers(path)
                if known_header is not None:
                    return loader_type(input_file=path, header=known_header)
        return None

    def __len__(self) -> int:
        """Number of files able to be loaded"""
        return len(self._input_loaders)

    def __iter__(self) -> Generator[FileLoaderInterface, None, None]:
        for loader in self._input_loaders:
            yield loader
