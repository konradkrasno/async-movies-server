""" Contains models for movies-database. """

from typing import *

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    Text,
    Float,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship

Base = declarative_base()


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Genre(name='%s')>" % (self.name,)


class ProductionCompany(Base):
    __tablename__ = "production_companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<ProductionCompany(name='%s')>" % (self.name,)


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    iso_3166_1 = Column(String, unique=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Country(name='%s')>" % (self.name,)


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    iso_639_1 = Column(String, unique=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Language(name='%s')>" % (self.name,)


movie_metadata_association_table = Table(
    "movie_metadata_association",
    Base.metadata,
    Column("movies_metadata", Integer, ForeignKey("movies_metadata.id")),
    Column("genres", Integer, ForeignKey("genres.id")),
    Column("production_companies", Integer, ForeignKey("production_companies.id")),
    Column("countries", Integer, ForeignKey("countries.id")),
    Column("languages", Integer, ForeignKey("languages.id")),
)


class MovieMetadata(Base):
    __tablename__ = "movies_metadata"

    id = Column(Integer, primary_key=True)
    adult = Column(Boolean)
    budget = Column(Integer)
    genres = relationship("Genre", secondary=movie_metadata_association_table)
    homepage = Column(String)
    original_language = Column(String)
    original_title = Column(String)
    overview = Column(Text)
    popularity = Column(Float)
    poster_path = Column(String)
    production_companies = relationship(
        "ProductionCompany", secondary=movie_metadata_association_table
    )
    production_countries = relationship(
        "Country", secondary=movie_metadata_association_table
    )
    release_date = Column(Date)
    revenue = Column(Integer)  # TODO maybe BigInteger
    runtime = Column(Integer)
    spoken_languages = relationship(
        "Language", secondary=movie_metadata_association_table
    )
    tagline = Column(Text)
    title = Column(String)
    vote_average = Column(Float)
    vote_count = Column(Integer)

    def __repr__(self):
        return "<MovieMetadata(title='%s')>" % (self.title,)

    @classmethod
    def create(cls, *args: Any) -> Base:
        pass

    def json(self) -> Dict:
        return {**self}
