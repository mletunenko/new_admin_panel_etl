from datetime import datetime
from logging import getLogger

import backoff
import django
from django.conf import settings
from django.db import OperationalError
from django.db.models import Q
from movies.models import (FilmWork,
                           Genre,
                           GenreFilmWork,
                           Person,
                           PersonFilmWork)

logger = getLogger(__name__)


class DataFetcher:
    @backoff.on_exception(backoff.expo, [django.db.OperationalError, django.db.utils.OperationalError], max_tries=3)
    def get_filmwork_query_set(self, from_date: datetime=None):
        try:
            base_qs = FilmWork.objects.order_by('id')
            if not from_date:
                return base_qs
            else:
                modified_by_genre_film_work_ids_qs = GenreFilmWork.objects.filter(genre__modified__gt=from_date).values_list('film_work_id', flat=True)
                modified_by_person_film_work_ids_qs = PersonFilmWork.objects.filter(person__modified__gt=from_date).values_list('film_work_id', flat=True)
                modified_ids_qs = modified_by_genre_film_work_ids_qs.union(modified_by_person_film_work_ids_qs)
                return base_qs.filter(Q(modified__gte=from_date)| Q(id__in=modified_ids_qs))
        except OperationalError as e:
            logger.error(f'{datetime.now()} Нет соединения с базой данных: {e}')
            raise e

    def get_filmwork_dict(self, filmwork):
        directors_names = []
        actors_names = []
        writers_names = []
        directors = []
        actors = []
        writers = []
        genres = [{'id':str(genre.id), 'name': genre.name} for genre in filmwork.genres.all()]
        m2m = filmwork.personfilmwork_set.select_related('person')
        for relation in m2m:
            person_dict = {
                'id': str(relation.person.id),
                'full_name': relation.person.full_name
            }
            match relation.role:
                case 'actor':
                    actors_names.append(relation.person.full_name)
                    actors.append(person_dict)
                case 'director':
                    directors_names.append(relation.person.full_name)
                    directors.append(person_dict)
                case 'writer':
                    writers_names.append(relation.person.full_name)
                    writers.append(person_dict)
        return {
            'id': str(filmwork.id),
            'imdb_rating': filmwork.rating,
            'genres': genres,
            'title': filmwork.title,
            'description': filmwork.description,
            'directors_names': directors_names,
            'actors_names': actors_names,
            'writers_names': writers_names,
            'directors': directors,
            'actors': actors,
            'writers': writers,
        }

    def get_filmwork_batch(self, from_date: datetime=None):
        qs = self.get_filmwork_query_set(from_date)
        offset = 0
        while result := qs[offset:offset+settings.PG_TO_ES_BATCH_SIZE]:
            batch = []
            for filmwork in result:
                obj = self.get_filmwork_dict(filmwork)
                batch.append(obj)
            yield batch
            offset += settings.PG_TO_ES_BATCH_SIZE


    @backoff.on_exception(backoff.expo, [django.db.OperationalError, django.db.utils.OperationalError], max_tries=3)
    def get_genre_query_set(self, from_date: datetime=None):
        try:
            base_qs = Genre.objects.order_by('id').values('id', 'name', 'description')
            if not from_date:
                return base_qs
            else:
                return base_qs.filter(modified__gte=from_date)
        except OperationalError as e:
            logger.error(f'{datetime.now()} Нет соединения с базой данных: {e}')
            raise e

    def get_genre_batch(self, from_date: datetime = None):
        qs = self.get_genre_query_set(from_date)
        offset = 0
        while result := qs[offset:offset + settings.PG_TO_ES_BATCH_SIZE]:
            batch = []
            for genre in result:
                obj = {
                    'id': str(genre['id']),
                    'name': genre['name'],
                    'description': genre['description']
                }
                batch.append(obj)
            yield batch
            offset += settings.PG_TO_ES_BATCH_SIZE

    @backoff.on_exception(backoff.expo, [django.db.OperationalError, django.db.utils.OperationalError], max_tries=3)
    def get_person_query_set(self, from_date: datetime=None):
        try:
            base_qs = Person.objects.order_by('id').values('id', 'full_name')
            if not from_date:
                return base_qs
            else:
                return base_qs.filter(modified__gte=from_date)
        except OperationalError as e:
            logger.error(f'{datetime.now()} Нет соединения с базой данных: {e}')
            raise e

    def get_person_batch(self, from_date: datetime = None):
        qs = self.get_person_query_set(from_date)
        offset = 0
        while result := qs[offset:offset + settings.PG_TO_ES_BATCH_SIZE]:
            batch = []
            for person in result:
                obj = {
                    'id': str(person['id']),
                    'full_name': person['full_name']
                }
                batch.append(obj)
            yield batch
            offset += settings.PG_TO_ES_BATCH_SIZE
