from datetime import datetime
from logging import getLogger


import backoff
import django
from django.conf import settings
from django.db import OperationalError
from django.db.models import Q
from movies.models import FilmWork, Genre, Person


logger = getLogger(__name__)

class DataFetcher:
    # @backoff.on_exception(backoff.expo, django.db.OperationalError, max_tries=10)
    def get_filmwork_query_set(self, from_date: datetime=None):
        try:
            if not from_date:
                return FilmWork.objects.prefetch_related('genres', 'personfilmwork_set').order_by('id').all()
            else:
                modified_genre_id_list = [str(record['id']) for record in Genre.objects.filter(modified__gte=from_date).values()]
                modified_person_id_list = [str(record['id']) for record in Person.objects.filter(modified__gte=from_date).values()]
                return (FilmWork.objects
                        .prefetch_related('genres', 'personfilmwork_set')
                        .order_by('id')
                        .filter(Q(modified__gte=from_date)|
                                Q(genres__id__in=modified_genre_id_list)|
                                Q(persons__id__in=modified_person_id_list))
                        .distinct())
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
        m2m = filmwork.personfilmwork_set.select_related('person')
        for relation in m2m:
            person_dict = {
                'id': str(relation.person.id),
                'name': relation.person.full_name
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
            'genres': [genre.name for genre in filmwork.genres.all()],
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
