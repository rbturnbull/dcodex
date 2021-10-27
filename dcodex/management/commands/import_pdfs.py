from django.core.management.base import BaseCommand, CommandError
from imagedeck.models import Deck
from dcodex.models import Manuscript, PDF


class Command(BaseCommand):
    def handle(self, *args, **options):
        Deck.import_glob(
            destination=options["destination"],
            pattern=options["pattern"],
            deck_name=options.get("deck"),
            owner=options.get("owner"),
        )

    def handle(self, *args, **options):
        for pdf in PDF.objects.all():
            print(pdf)
            deck_name = str(pdf)
            if Deck.objects.filter(name=deck_name).count() > 0:
                print(f"Already has {deck_name}")
                continue

            destination = deck_name.replace(".pdf", "")
            pattern = f"{deck_name}-\d+.jpg"
            owner = "rob"

            Deck.import_regex(
                destination=destination,
                source_dir="media/facsimiles/",
                pattern=pattern,
                deck_name=deck_name,
                owner=owner,
            )
            # return
