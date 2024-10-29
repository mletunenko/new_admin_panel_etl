from typing import List

from pydantic import BaseModel


class GenreModel(BaseModel):
    id: str


class PersonModel(BaseModel):
    id: str
    name: str


class FilmWorkModel(BaseModel):
    id: str
    imdb_rating: float | None
    genres: List[str]
    title: str
    description: str | None
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: List[PersonModel]
    actors: List[PersonModel]
    writers: List[PersonModel]
