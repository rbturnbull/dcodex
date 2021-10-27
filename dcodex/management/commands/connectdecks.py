from django.core.management.base import BaseCommand, CommandError
from imagedeck.models import Deck
from dcodex.models import Manuscript, PDF, VerseLocation, DeckMembership
from filer.models import Image as FilerImage


class Command(BaseCommand):
    def handle(self, *args, **options):
        for manuscript in Manuscript.objects.filter(imagedeck=None):
            print(f"Manuscript {manuscript} has no image deck")
            pdfs = PDF.objects.filter(verselocation__manuscript=manuscript).distinct()
            print(pdfs)
            if not pdfs:
                continue
            if pdfs.count() == 1:
                pdf = pdfs.first()
                deck_name = str(pdf)
                print(f"Connecting {deck_name}")
                deck = Deck.objects.get(name=deck_name)
                manuscript.imagedeck = deck
                manuscript.save()
            else:
                deck_names_to_combine = [str(pdf) for pdf in pdfs]
                deck = Deck.combine(str(manuscript.siglum), deck_names_to_combine)
                manuscript.imagedeck = deck
                manuscript.save()

                for location in VerseLocation.objects.filter(manuscript=manuscript):
                    filename = location.pdf.image_path(location.page).split("/")[-1]
                    print(location, filename)

                    image = FilerImage.objects.filter(
                        original_filename=filename
                    ).first()

                    deck_membership = DeckMembership.objects.filter(
                        deck=manuscript.imagedeck, image=image.deckimagefiler
                    ).first()
                    deck_membership.rank = location.verse.id
                    deck_membership.save()

                    print(image, deck_membership)
                    location.deck_membership = deck_membership
                    location.save()
