from django.core.management.base import BaseCommand, CommandError
from dcodex.management.commands._dcodex_commands import ManuscriptCommand


class Command(ManuscriptCommand):
    help = "Outputs a LaTeX representation of a manuscript."

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--baseurl",
            type=str,
            help="A base url to a D-Codex site which can display the verse transcriptions.",
        )

    def handle_manuscript(self, manuscript, *args, **options):
        latex = manuscript.latex(baseurl=options.get("baseurl"))
        print(latex)
