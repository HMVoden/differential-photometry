from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, Text,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import MetaData

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


class StarDB(Base):
    __tablename__ = "stars"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    x = Column("x", Integer)
    y = Column("y", Integer)

    timeseries = relationship(
        "StarDBTimeseries",
        back_populates="star",
    )

    label = relationship("StarDBLabel", back_populates="star")

    def __repr__(self):
        return f"StarDB(id:'{self.id}',x:'{self.x}',y:'{self.y}')"


class StarDBLabel(Base):
    __tablename__ = "label"
    name = Column("name", Text, primary_key=True)
    dataset = Column("dataset", Text, primary_key=True)
    idref = Column(Integer, ForeignKey("stars.id"))

    star = relationship("StarDB", back_populates="label")

    __table_args__ = (UniqueConstraint("name", "dataset", name="_name_dataset_unique"),)

    def __repr__(self):
        return f"StarDBLabel(id:'{self.idref}',dataset:'{self.dataset}',name:'{self.name}')"


class StarDBTimeseries(Base):
    __tablename__ = "timeseries"
    tsid = Column("tsid", Integer, primary_key=True, autoincrement=True)
    time = Column("time", DateTime)
    mag = Column("magnitude", Float)
    error = Column("error", Float)
    idref = Column(Integer, ForeignKey("stars.id"))

    star = relationship("StarDB", back_populates="timeseries")

    def __repr__(self):
        return f"StarDBTimeseries('id:{self.idref}',time:'{self.time}',mag:'{self.mag}', error:'{self.error}')"
