import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to pause execution until database is available
    """

    def handle(self, *args, **options):
        self.stdout.write('Waiting for Docker DB service...')
        db_conn = None

        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stderr.write(self.style.WARNING(
                    'Docker DB unavailable, waiting 1 seconds'))
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Connected to DB successfully'))
