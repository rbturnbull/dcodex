from django.core.management.base import BaseCommand, CommandError
from imagedeck.models import DeckMembership
from filer.models import Image as FilerImage
from imagedeck.models import Deck
import re
from dcodex.models import VerseLocation, Page, FolioRef


class Command(BaseCommand):
    def handle(self, *args, **options):
        # deck = Deck.objects.get(name="S71+")
        # for membership in deck.deckmembership_set.all():
        #     filename = str(membership.image)
        #     rank_regex="(\d+)"
        #     integer_matches = re.findall(rank_regex, str(filename) )
        #     rank = int(integer_matches[-1]) if integer_matches else None

        #     if "Parchment" in filename:
        #         rank += 1000

        #     membership.rank = rank
        #     print(filename, rank)
        #     membership.save()

        # deck = Deck.objects.get(name="N6")
        # for membership in deck.deckmembership_set.all():
        #     filename = str(membership.image)
        #     rank_regex="(\d+)"
        #     integer_matches = re.findall(rank_regex, str(filename) )
        #     rank = int(integer_matches[-1]) if integer_matches else None

        #     if "5.pdf" in filename:
        #         rank += 1000
        #     if "63.pdf" in filename:
        #         rank += 2000

        #     membership.rank = rank
        #     membership.save()

        deck = Deck.objects.get(name="L")
        for membership in deck.deckmembership_set.all():
            filename = str(membership.image)
            rank_regex = "(\d+)"
            integer_matches = re.findall(rank_regex, str(filename))
            rank = int(integer_matches[-1]) if integer_matches else None

            if "14.pdf" in filename:
                rank += 1000
            if "16.pdf" in filename:
                rank += 2000

            membership.rank = rank
            membership.save()

        # deck = Deck.objects.get(name="N15+")
        # for membership in deck.deckmembership_set.all():
        #     filename = str(membership.image)
        #     rank_regex="(\d+)"
        #     integer_matches = re.findall(rank_regex, str(filename) )
        #     rank = int(integer_matches[-1]) if integer_matches else None

        #     if "15.pdf" in filename and rank > 74:
        #         rank += 100000

        #         membership.rank = rank
        #         membership.save()
