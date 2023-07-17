from django.core.management.base import BaseCommand, CommandError
from dcodex.models import Manuscript
import pandas as pd


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "csv",
            type=str,
            help="A CSV file with dates. Required columns: `siglum`, `origin_date_earliest`, `origin_date_latest`.",
        )

    def handle(self, *args, **options):
        df = pd.read_csv(options["csv"])
        for _, row in df.iterrows():
            manuscript = Manuscript.find(row["siglum"])
            assert manuscript is not None
            manuscript.origin_date_earliest = row["origin_date_earliest"]
            manuscript.origin_date_latest = row["origin_date_latest"]
            manuscript.save()
            print(f"{manuscript.siglum}: {manuscript.origin_date_earliest}–{manuscript.origin_date_latest}")