import json

from _datetime import datetime
from logging import getLogger

from elasticsearch import Elasticsearch, helpers


logger = getLogger(__name__)


class ElasticsearchConnector:
    def __init__(self, hosts, index, schema_file):
        self.client = Elasticsearch(hosts)
        self.index = index
        self.schema_file = schema_file

    def create_index(self):
        with open(self.schema_file) as f:
            schema = json.load(f)
        self.client.indices.create(index=self.index, settings=schema['settings'], mappings=schema['mappings'])

    def load_data(self, batch):
        documents = [
            {
                '_index': self.index,
                '_id': item['id'],
                '_source': item
            }
            for item in batch
        ]
        result = helpers.bulk(self.client, documents)
        logger.warning(f'{datetime.now()} {result[0]} записей обновлено')
