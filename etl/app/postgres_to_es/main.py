import signal
import sys
import time
from logging import getLogger

from django.conf import settings
from django.utils import timezone
from postgres_to_es.data_synchronizer import DataSyncService
from postgres_to_es.state import StateService

logger = getLogger(__name__)
shutdown_flag = False


def signal_handler(sig, frame):
    global shutdown_flag
    print("Получен сигнал завершения работы. Завершаемся...")
    shutdown_flag = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def run():
    syncronizer = DataSyncService()

    elastic_dsl = {
        'hosts': settings.ELASTIC_URL,
        'index': settings.ES_INDEX,
        'schema_file': settings.ES_SCHEMA_FILE,
    }

    syncronizer.create_es_connector(**elastic_dsl)
    syncronizer.prepare_index()
    syncronizer.create_data_fetcher()
    state = StateService(settings.PG_TO_ES_STATE_FILE_NAME)
    timestamp = state.get_value('timestamp')

    logger.info('Сервис синхронизации pg_to_es запущен')

    while not shutdown_flag:
        new_timestamp = str(timezone.now())
        logger.info('Запущена итерация синхронизации')
        syncronizer.transfer_data(timestamp)
        state.set_value('timestamp', new_timestamp)
        timestamp = new_timestamp
        logger.info('Завершена итерация синхронизации')
        for _ in range(3600):
            if shutdown_flag:
                logger.info('Завершение работы сервиса postgres_to_es')
                sys.exit()
            time.sleep(1)


if __name__ == '__main__':
    run()
