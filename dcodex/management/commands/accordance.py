from django.core.management.base import BaseCommand, CommandError
from ._dcodex_commands import ManuscriptCommand


class Command(ManuscriptCommand):
    help = "Outputs a text representation of a manuscript as an Accordance User Bible."

    def handle_manuscript(self, manuscript, *args, **options):
        print(manuscript.accordance())
