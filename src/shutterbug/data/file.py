import logging
from pathlib import Path
from typing import Generator, List, Type, Union

from attr import define, field
from shutterbug.data.interfaces.external import InputInterface, FileLoaderInterface
from shutterbug.data.csv.loader import CSVLoader

_TYPES: List[Type[FileLoaderInterface]] = [CSVLoader]


@define
class FileInput(InputInterface):
    path: Path = field()
    _input_files: List[Path] = field(init=False)

    def __attrs_post_init__(self):
        all_files = self._get_files_from_path(self.path)
        self._input_files = all_files

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
                        f"Loader unable to load file {path.name}, received error:"
                    )
                    logging.exception(e)
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
