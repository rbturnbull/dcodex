from django.core.management.base import BaseCommand, CommandError
from dcodex.management.commands._dcodex_commands import ManuscriptCommand

class Command(ManuscriptCommand):
    help = 'Outputs a LaTeX representation of a manuscript.'

    def handle_manuscript(self, manuscript, *args, **options):
        print(manuscript.latex())