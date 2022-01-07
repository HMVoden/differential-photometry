from sqlalchemy import (Column, DateTime, Float, ForeignKey, Index, Integer,
                        Text)
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
    __tablename__ = "star"
    name = Column("name", Text, primary_key=True)
    dataset = Column("dataset", Text, primary_key=True)
    x = Column("x", Integer)
    y = Column("y", Integer)

    timeseries = relationship(
        "timeseries",
        order_by="desc(timeseries.star_name)",
        back_populates="star",
    )


class StarDBTimeseries(Base):
    __tablename__ = "timeseries"
    star_name = Column(Text, ForeignKey("star.name"), primary_key=True)
    star_dataset = Column(Text, ForeignKey("star.dataset"), primary_key=True)
    time = Column("time", DateTime, primary_key=True)
    mag = Column("magnitude", Float)
    error = Column("error", Float)

    star = relationship("star", back_populates="timeseries")
