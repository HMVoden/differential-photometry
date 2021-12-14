def test_filter_unreadable_paths(files_with_good_count):
    test_count, test_files = files_with_good_count
    filtered_files = list(_filter_unreadable_paths(test_files))
    filtered_count = len(filtered_files)
    assert test_count == filtered_count


def test_get_file_count(files_with_good_count):
    test_count, test_files = files_with_good_count
    filtered_count = get_readable_file_count(test_files)
    assert test_count == filtered_count


def test_files_from_paths(existing_file_list):
    flat_files = _get_files_from_paths(existing_file_list)
    # all are present
    assert all(map(lambda x: x in existing_file_list, flat_files))
    # all are existing files
    assert all(map(lambda x: x.is_file(), flat_files))


def test_files_from_dir(existing_dir):
    flat_files = _get_files_from_paths([existing_dir])
    assert len(flat_files) == 0
