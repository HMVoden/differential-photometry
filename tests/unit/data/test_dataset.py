
from hypothesis import given
from shutterbug.data.dataset import Dataset
from shutterbug.data.db.reader import DBReader
from shutterbug.data.db.writer import DBWriter
from shutterbug.data.star import Star
from tests.unit.data.db.db_test_tools import sqlite_memory
from tests.unit.data.hypothesis_stars import star


@given(star())
def test_dataset_update_read(star: Star):
    with sqlite_memory(future=True) as session:
        writer = DBWriter(dataset="test", session=session)
        reader = DBReader(dataset="test", session=session)
        dataset = Dataset(name="test", reader=reader, writer=writer)
        writer.write(star)
        for date in star.timeseries.features:
            star.timeseries.add_feature(
                dt=date, name="Inverse Von Neumann", value=123.0
            )
            star.timeseries.add_feature(dt=date, name="IQR", value=567.0)
        star.timeseries.differential_error = star.timeseries.error
        star.timeseries.differential_magnitude = star.timeseries.magnitude
        dataset.update(star)
        read_star = next(dataset.__iter__())
        assert read_star == star
        assert len(star.timeseries.features) == len(read_star.timeseries.features)
        for date in star.timeseries.features.keys():
            assert date in read_star.timeseries.features.keys()
            assert read_star.timeseries.features[date]["Inverse Von Neumann"] == 123.0
            assert read_star.timeseries.features[date]["IQR"] == 567.0


@given(star())
def test_dataset_variable_update_read(star: Star):
    with sqlite_memory(future=True) as session:
        writer = DBWriter(dataset="test", session=session)
        reader = DBReader(dataset="test", session=session)
        dataset = Dataset(name="test", reader=reader, writer=writer)
        writer.write(star)
        for date in star.timeseries.features:
            star.timeseries.add_feature(
                dt=date, name="Inverse Von Neumann", value=123.0
            )
            star.timeseries.add_feature(dt=date, name="IQR", value=567.0)
        star.timeseries.differential_error = star.timeseries.error
        star.timeseries.differential_magnitude = star.timeseries.magnitude
        star.variable = True
        dataset.update(star)
        read_star = next(dataset.variable)
        assert read_star == star
        assert len(star.timeseries.features) == len(read_star.timeseries.features)
        for date in star.timeseries.features.keys():
            assert date in read_star.timeseries.features.keys()
            assert read_star.timeseries.features[date]["Inverse Von Neumann"] == 123.0
            assert read_star.timeseries.features[date]["IQR"] == 567.0
