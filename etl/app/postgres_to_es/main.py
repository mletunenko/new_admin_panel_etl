from datetime import datetime
import time
from logging import getLogger

from django.conf import settings
from postgres_to_es.data_synchronizer import DataSyncService

from postgres_to_es.state import StateService


logger = getLogger(__name__)

def run():
    syncronizer = DataSyncService()

    elastic_dsl = {
        'hosts': settings.ELASTIC_URL,
        'index':settings.ES_INDEX,
        'schema_file': settings.ES_SCHEMA_FILE,
    }

    syncronizer.create_es_connector(**elastic_dsl)
    syncronizer.prepare_index()
    syncronizer.create_data_fetcher()
    state = StateService(settings.PG_TO_ES_STATE_FILE_NAME)
    timestamp = state.get_value('timestamp')

    logger.info('Сервис синхронизации pg_to_es запущен')

    while True:
        new_timestamp = str(datetime.now())
        logger.info('Запущена итерация синхронизации')
        syncronizer.transfer_data(timestamp)
        state.set_value('timestamp', new_timestamp)
        timestamp = new_timestamp
        logger.info('Завершена итерация синхронизации')
        time.sleep(30)

    logger.info('Сервис синхронизации pg_to_es закончил работу')


if __name__ == '__main__':
    run()
