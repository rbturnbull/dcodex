from django.core.management.base import BaseCommand, CommandError
from ._dcodex_commands import ManuscriptCommand


class Command(ManuscriptCommand):
    help = "Outputs a TEI representation of a manuscript."

    def handle_manuscript(self, manuscript, *args, **options):
        print(manuscript.tei_string())
