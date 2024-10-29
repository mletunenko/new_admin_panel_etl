from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ['get']

    def get_queryset(self):
        return FilmWork.objects.prefetch_related('genres', 'personfilmwork_set')

    def get(self, *args, **kwargs):
        context = self.get_context_data(*args, **kwargs)
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *args, **kwargs):
        queryset = self.get_queryset()
        paginator, page, page_queryset, is_paginated = self.paginate_queryset(queryset, self.paginate_by)

        json_queryset = []

        for film_work in page_queryset:
            # для ревьюера: такие сложные цепочки нужны что бы добраться до поля role
            m2m = film_work.personfilmwork_set.select_related('person')
            actors = []
            directors = []
            writers = []
            for relation in m2m:
                match relation.role:
                    case 'actor':
                        actors.append(relation.person.full_name)
                    case 'director':
                        directors.append(relation.person.full_name)
                    case 'writer':
                        writers.append(relation.person.full_name)

            obj = {
                'id': str(film_work.id),
                'description': film_work.description,
                'creation_date': film_work.creation_date,
                'rating': film_work.rating,
                'type': film_work.type,
                'genres': [genre.name for genre in film_work.genres.all()],
                'actors': actors,
                'directors': directors,
                'writers': writers,
            }
            json_queryset.append(obj)

        context = {
            'count': queryset.count(),
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(json_queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, *args, **kwargs):
        pk = kwargs['pk']
        try:
            film_work = self.get_queryset().get(id=pk)
        except ObjectDoesNotExist:
            return {'detail': 'No Model matches the given query.'}
        # для ревьюера: такие сложные цепочки нужны что бы добраться до поля role
        m2m = film_work.personfilmwork_set.select_related('person')
        actors = []
        directors = []
        writers = []
        for relation in m2m:
            match relation.role:
                case 'actor':
                    actors.append(relation.person.full_name)
                case 'director':
                    directors.append(relation.person.full_name)
                case 'writer':
                    writers.append(relation.person.full_name)
        obj = {
            'id': str(film_work.id),
            'description': film_work.description,
            'creation_date': film_work.creation_date,
            'rating': film_work.rating,
            'type': film_work.type,
            'genres': [genre.name for genre in film_work.genres.all()],
            'actors': actors,
            'directors': directors,
            'writers': writers,
        }
        return obj
