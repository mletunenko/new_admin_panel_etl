import json
from logging import getLogger

import backoff
from _datetime import datetime
from elastic_transport import ConnectionError
from elasticsearch import Elasticsearch, helpers

logger = getLogger(__name__)


class ElasticsearchConnector:
    def __init__(self, hosts, indexes, schemas):
        self.client = Elasticsearch(hosts)
        self.indexes = indexes
        self.schemas = schemas

    def create_index(self, index):
        with open(self.schemas[index]) as f:
            schema = json.load(f)
        self.client.indices.create(index=index, settings=schema['settings'], mappings=schema['mappings'])

    @backoff.on_exception(backoff.expo, ConnectionError, max_tries=15)
    def load_data(self, batch, index):
        documents = [
            {
                '_index': index,
                '_id': item['id'],
                '_source': item
            }
            for item in batch
        ]
        try:
            result = helpers.bulk(self.client, documents)
            logger.warning(f'{datetime.now()} {result[0]} записей обновлено')
            for error in result[1]:
                logger.error(f'{datetime.now()} При обновлении возникла ошибка: {error}')
        except ConnectionError as e:
            logger.error(f'{datetime.now()} Не удалось установить соединение с Elasticsearch: {e}')
            raise e
