""" Contains models for movies-database. """

from typing import *

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    Text,
    Float,
    ForeignKey,
    Date,
    ARRAY,
    or_,
)

Base = declarative_base()


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Genre(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, name: str) -> Base:
        return session.query(cls).filter(cls.name == name).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["name"])
        if query:
            return query
        return cls(**kwargs)


class ProductionCompany(Base):
    __tablename__ = "production_companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<ProductionCompany(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, name: str) -> Base:
        return session.query(cls).filter(cls.name == name).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["name"])
        if query:
            return query
        return cls(**kwargs)


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    iso_3166_1 = Column(String, unique=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Country(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, iso_3166_1: str, name: str) -> Base:
        return (
            session.query(cls)
            .filter(
                or_(
                    cls.iso_3166_1 == iso_3166_1,
                    cls.name == name,
                )
            )
            .first()
        )

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["iso_3166_1"], kwargs["name"])
        if query:
            return query
        return cls(**kwargs)


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    iso_639_1 = Column(String, unique=True)
    name = Column(String, unique=True)

    def __repr__(self):
        return "<Language(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, iso_639_1: str, name: str) -> Base:
        return (
            session.query(cls)
            .filter(
                or_(
                    cls.iso_639_1 == iso_639_1,
                    cls.name == name,
                )
            )
            .first()
        )

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["iso_639_1"], kwargs["name"])
        if query:
            return query
        return cls(**kwargs)


movie_metadata_association_table = Table(
    "movie_metadata_association",
    Base.metadata,
    Column("movies_metadata", BigInteger, ForeignKey("movies_metadata.id")),
    Column("genres", Integer, ForeignKey("genres.id")),
    Column("production_companies", Integer, ForeignKey("production_companies.id")),
    Column("countries", Integer, ForeignKey("countries.id")),
    Column("languages", Integer, ForeignKey("languages.id")),
)


class MovieMetadata(Base):
    __tablename__ = "movies_metadata"

    id = Column(BigInteger, primary_key=True)
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

    def json(self) -> Dict:
        return {**self}

    @classmethod
    def get(cls, session: Session, _id: int) -> Base:
        return session.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["id"])
        if query:
            return query
        return cls(**kwargs)


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(Integer)
    profile_path = Column(String)
    character_id = Column(Integer, ForeignKey("characters.id"))
    character = relationship("Character", back_populates="actor")

    def __repr__(self):
        return "<Actor(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, _id: int) -> Base:
        return session.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["id"])
        if query:
            return query
        return cls(**kwargs)


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True)
    character = Column(String)
    order = Column(Integer)
    actor = relationship("Actor", uselist=False, back_populates="character")
    movie_id = Column(Integer, ForeignKey("movies_metadata.id"))

    @classmethod
    def create(cls, session: Session, **kwargs: Any) -> Base:
        return cls(**kwargs)


class CrewMember(Base):
    __tablename__ = "crew_members"

    id = Column(Integer, primary_key=True)
    # crew_ids = relationship("Crew", secondary=crew_members_association_table)
    name = Column(String)
    gender = Column(Integer)
    profile_path = Column(String)
    crew_id = Column(Integer, ForeignKey("crew.id"))
    crew = relationship("Crew", back_populates="crew_member")

    def __repr__(self):
        return "<CrewMember(name='%s')>" % (self.name,)

    @classmethod
    def get(cls, session: Session, _id: int) -> Base:
        return session.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["id"])
        if query:
            return query
        return cls(**kwargs)


class Crew(Base):
    __tablename__ = "crew"

    id = Column(Integer, primary_key=True)
    department = Column(String)
    job = Column(String)
    crew_member = relationship("CrewMember", uselist=False, back_populates="crew")
    movie_id = Column(Integer, ForeignKey("movies_metadata.id"))

    @classmethod
    def create(cls, session: Session, **kwargs: Any) -> Base:
        return cls(**kwargs)


class Keywords(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies_metadata.id"))
    keywords = Column(ARRAY(String))

    def __repr__(self):
        return "<Keywords(keywords='%s')>" % (self.keywords,)

    @classmethod
    def get(cls, session: Session, movie_id: int) -> Base:
        return session.query(cls).filter(cls.movie_id == movie_id).first()

    @classmethod
    def get_or_create(cls, session: Session, **kwargs: Any) -> Base:
        query = cls.get(session, kwargs["movie_id"])
        if query:
            return query
        return cls(**kwargs)
