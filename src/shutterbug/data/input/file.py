def _filter_unreadable_paths(paths: List[Path]) -> Iterator:
    return filter(_is_accepted_format, paths)


def _get_files_from_path(path: Path) -> List[Path]:
    result = []
    if path.is_dir():
        files = [x for x in path.iterdir() if x.is_file()]
        result.extend(files)
    elif path.is_file():
        result.append(path)
    return result


def _get_files_from_paths(paths: List[Path]):
    result = []
    for path in paths:
        result.extend(_get_files_from_path(path))
    return result


def get_readable_file_count(paths: List[Path]) -> int:
    paths = _get_files_from_paths(paths)
    return len(list(_filter_unreadable_paths(paths)))
