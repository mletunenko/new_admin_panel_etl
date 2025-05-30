from datetime import datetime
from logging import getLogger

import backoff
from elastic_transport import ConnectionError
from postgres_to_es.data_fetcher import DataFetcher
from postgres_to_es.elastic_connector import ElasticsearchConnector
from postgres_to_es.pydantic_models import (FilmWorkModel,
                                            GenreModel,
                                            PersonModel)
from pydantic.v1 import ValidationError
from pydantic_core._pydantic_core import ValidationError

logger = getLogger(__name__)


class DataSyncService:

    def __init__(self):
        self.es_connector = None
        self.data_fetcher = None

    def create_es_connector(self, **kwargs):
        self.es_connector = ElasticsearchConnector(**kwargs)

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=15)
    def prepare_index(self):
        try:
            es = self.es_connector
            for index in es.indexes:
                if not es.client.indices.exists(index=index):
                    es.create_index(index)
        except ConnectionError as e:
            logger.error(f'{datetime.now()} Не удалось установить соединение с Elasticsearch: {e}')
            raise e

    def create_data_fetcher(self):
        self.data_fetcher = DataFetcher()

    def validate_filmwork_bacth(self, batch):
        try:
            transformed_batch = [FilmWorkModel(**filmwork_dict) for filmwork_dict in batch]
        except ValidationError as e:
            logger.error(f'Ошибка валидации, партия данных не будет отправлена: {e}')
            return []
        return [item.model_dump() for item in transformed_batch]

    def validate_genre_bacth(self, batch):
        try:
            transformed_batch = [GenreModel(**genre_dict) for genre_dict in batch]
        except ValidationError as e:
            logger.error(f'Ошибка валидации, партия данных не будет отправлена: {e}')
            return []
        return [item.model_dump() for item in transformed_batch]

    def validate_person_bacth(self, batch):
        try:
            transformed_batch = [PersonModel(**person_dict) for person_dict in batch]
        except ValidationError as e:
            logger.error(f'Ошибка валидации, партия данных не будет отправлена: {e}')
            return []
        return [item.model_dump() for item in transformed_batch]



    def transfer_data(self, timestamp):
        for batch in self.data_fetcher.get_filmwork_batch(timestamp):
            validated_batch = self.validate_filmwork_bacth(batch)
            self.es_connector.load_data(validated_batch, 'movies')

        for batch in self.data_fetcher.get_genre_batch(timestamp):
            validated_batch = self.validate_genre_bacth(batch)
            self.es_connector.load_data(validated_batch, 'genres')

        for batch in self.data_fetcher.get_person_batch(timestamp):
            validated_batch = self.validate_person_bacth(batch)
            self.es_connector.load_data(validated_batch, 'persons')

