from dcodex.models import *


def run(*args):
    family_name = "All"
    if len(args):
        family_name = args[0]

    family, _ = Family.objects.get_or_create(name=family_name)
    affiliation, _ = AffiliationAll.objects.get_or_create(name=family_name)
    affiliation.families.add(family)
    for manuscript in Manuscript.objects.all():
        affiliation.manuscripts.add(manuscript)
