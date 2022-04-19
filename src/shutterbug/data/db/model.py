from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import DateTime

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)


class StarDBDataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column("dataset", Text, unique=True)

    stars = relationship("StarDB", cascade="all, delete")

    def __repr__(self):
        return f"StarDBDataset(id:'{self.id}', name:'{self.name}')"


class StarDB(Base):
    __tablename__ = "stars"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column("name", Text)
    dsid_ref = Column("dsid", Integer, ForeignKey("dataset.id"))
    x = Column("x", Integer)
    y = Column("y", Integer)
    magnitude_median = Column("magnitude_median", Float)
    variable = Column("variable", Boolean)

    dataset = relationship("StarDBDataset", back_populates="stars")

    timeseries = relationship(
        "StarDBTimeseries", cascade="all, delete", back_populates="star"
    )
    features = relationship(
        "StarDBFeatures", cascade="all, delete", back_populates="star"
    )

    UniqueConstraint("name", "dsid", name="name_per_dataset")

    def __repr__(self):
        return f"StarDB(id:'{self.id}',name:'{self.name}',dsid:'{self.dsid_ref}',magnitude median:'{self.magnitude_median}',is variable:{self.variable})"


class StarDBFeatures(Base):
    __tablename__ = "features"
    star_id = Column("id", Integer, ForeignKey("stars.id"), primary_key=True)
    ivn = Column(Float)
    iqr = Column(Float)
    star = relationship("StarDB", back_populates="features")


class StarDBTimeseries(Base):
    __tablename__ = "timeseries"
    tsid = Column("tsid", Integer, primary_key=True, autoincrement=True)
    star_id = Column("star_id", Integer, ForeignKey("stars.id"))
    time = Column("time", DateTime(timezone=True))
    mag = Column("magnitude", Float)
    error = Column("error", Float)
    adm = Column("adm", Float)  # different magnitude and error
    ade = Column("ade", Float)

    star = relationship("StarDB", back_populates="timeseries")

    def __repr__(self):
        return f"StarDBTimeseries('id:{self.tsid}',star_id:{self.star_id},time:'{self.time}',mag:'{self.mag}', error:'{self.error}',adm:'{self.adm}',ade:'{self.ade}')"
