import pytest
from hypothesis import given
from hypothesis.strategies import lists
from shutterbug.data.storage.db.reader import DBReader
from shutterbug.data.storage.db.writer import DBWriter
from tests.unit.data.db.db_test_tools import sqlalchemy_db
from tests.unit.data.hypothesis_stars import stars


@given(lists(stars(dataset="test"), min_size=1, unique_by=(lambda x: x.name)))
def test_reads_all(stars):
    with sqlalchemy_db() as db:
        # Unpack
        engine, _ = db
        writer = DBWriter(engine)

        reader = DBReader(dataset="test", engine=engine)
        star_names = []
        read_names = []
        # load DB for reading
        for star in stars:
            writer.write(star)
            # we're just going to make sure that the names are there
            star_names.append(star.name)

        for star_block in reader.all:
            print(star_block)
            for name in star_block["name"]:
                read_names.append(name)
        star_set = set(star_names)
        read_set = set(read_names)
        assert star_set == read_set
