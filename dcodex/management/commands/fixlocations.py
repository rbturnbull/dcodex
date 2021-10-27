from django.core.management.base import BaseCommand, CommandError
from imagedeck.models import DeckMembership
from filer.models import Image as FilerImage

from dcodex.models import VerseLocation, Page, FolioRef
from ._dcodex_commands import ManuscriptCommand


class Command(ManuscriptCommand):
    def handle_manuscript(self, manuscript, *args, **options):
        for location in VerseLocation.objects.filter(manuscript=manuscript):
            filename = location.pdf.image_path(location.page).split("/")[-1]
            print(location, filename)

            image = FilerImage.objects.filter(original_filename=filename).first()
            deck_membership = DeckMembership.objects.filter(
                deck=manuscript.imagedeck, image=image.deckimagefiler
            ).first()
            print(image, deck_membership)
            location.deck_membership = deck_membership
            location.save()

        for page in Page.objects.filter(manuscript=manuscript):
            filename = page.pdf.image_path(page.page).split("/")[-1]
            image = FilerImage.objects.filter(original_filename=filename).first()
            deck_membership = DeckMembership.objects.filter(
                deck=manuscript.imagedeck, image=image.deckimagefiler
            ).first()

            print(page)
            print(filename, deck_membership)
            FolioRef.objects.update_or_create(
                deck_membership=deck_membership, folio=page.folio, side=page.side
            )
