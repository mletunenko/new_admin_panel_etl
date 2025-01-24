from typing import List

from pydantic import BaseModel


class ShortGenreModel(BaseModel):
    id: str
    name: str


class GenreModel(ShortGenreModel):
    description: str | None


class PersonModel(BaseModel):
    id: str
    full_name: str


class FilmWorkModel(BaseModel):
    id: str
    imdb_rating: float | None
    genres: List[ShortGenreModel]
    title: str
    description: str | None
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: List[PersonModel]
    actors: List[PersonModel]
    writers: List[PersonModel]
