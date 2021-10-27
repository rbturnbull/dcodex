from django.core.management.base import BaseCommand, CommandError
from dcodex.models import Manuscript


class ManuscriptCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("siglum", type=str, help="The siglum of the manuscript.")

    def handle(self, *args, **options):
        siglum = options["siglum"]
        manuscript = Manuscript.find(siglum)
        if manuscript is None:
            raise CommandError(f"Cannot understand manuscript siglum '{siglum}'.")

        return self.handle_manuscript(manuscript, *args, **options)

    def handle_manuscript(self, manuscript, *args, **options):
        raise CommandError(
            f"The command does not implement the 'handle_manuscript' method."
        )
