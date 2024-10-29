from datetime import datetime
from logging import getLogger

import backoff
from elastic_transport import ConnectionError
from postgres_to_es.data_fetcher import DataFetcher
from postgres_to_es.elastic_connector import ElasticsearchConnector

from postgres_to_es.pydantic_models import FilmWorkModel
logger = getLogger(__name__)

class DataSyncService:

    def __init__(self):
        self.es_connector = None
        self.data_fetcher = None

    def create_es_connector(self, **kwargs):
        self.es_connector = ElasticsearchConnector(**kwargs)

    # @backoff.on_exception(backoff.expo, ConnectionError, max_tries=15)
    def prepare_index(self):
        try:
            es = self.es_connector
            if not es.client.indices.exists(index=es.index):
                es.create_index()
        except ConnectionError as e:
            logger.error(f'{datetime.now()} Не удалось установить соединение с Elasticsearch: {e}')
            raise e

    def create_data_fetcher(self):
        self.data_fetcher = DataFetcher()

    # @backoff.on_exception(backoff.expo, ConnectionError, max_tries=15)
    def transfer_data(self, timestamp):
        try:
            for batch in self.data_fetcher.get_filmwork_batch(timestamp):
                # transformed_batch = [FilmWorkModel(**filmwork_dict) for filmwork_dict in batch]
                self.es_connector.load_data(batch)
        except ConnectionError as e:
            logger.error(f'{datetime.now()} Не удалось установить соединение с Elasticsearch: {e}')
            raise e
