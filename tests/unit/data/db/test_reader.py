import pytest
from hypothesis import given
from hypothesis.strategies import lists
from shutterbug.data.storage.db.reader import DBReader
from shutterbug.data.storage.db.writer import DBWriter
from tests.unit.data.db.db_test_tools import sqlalchemy_db
from tests.unit.data.hypothesis_stars import stars


@given(
    lists(stars(dataset="test"), min_size=1, unique_by=(lambda x: x.name)),
    lists(stars(dataset="other"), min_size=1, unique_by=(lambda x: x.name)),
)
def test_init(stars, other):
    engine = sqlalchemy_db(future=False)
    writer = DBWriter(engine)
    star_names = []
    for star in stars:
        writer.write(star)
        star_names.append(star.name)
    for star in other:
        writer.write(star)
    reader = DBReader(dataset="test", engine=engine)

    assert all([True if x in reader._stars else False for x in star_names])
    assert len(reader._stars) == len(stars)


@given(
    lists(stars(dataset="test"), min_size=1, unique_by=(lambda x: x.name)),
    lists(stars(dataset="other"), min_size=1, unique_by=(lambda x: x.name)),
)
def test_reads_all(stars, other):
    engine = sqlalchemy_db(future=False)

    writer = DBWriter(engine)
    # load DB for reading
    star_names = []
    for star in stars:
        writer.write(star)
        # we're just going to make sure that the names are there
        star_names.append(star.name)
    for star in other:
        # so we can make sure we're only getting from our dataset
        writer.write(star)

    reader = DBReader(dataset="test", engine=engine)
    read_names = []
    datasets = []
    for star in reader.all:
        read_names.append(star["name"][0])
        datasets.append(star["dataset"][0])
    star_set = set(star_names)
    read_set = set(read_names)
    assert star_set == read_set
    assert len(set(datasets)) == 1
    assert len(star_set) == len(stars)
