from django.core.management.base import BaseCommand
from postgres_to_es.main import run


class Command(BaseCommand):
    help = "Synchronize Elasticsearch with Postgres "

    def handle(self, *args, **options):
        run()