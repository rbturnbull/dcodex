from dcodex.models import *


def run(*args):
    for manuscript in Manuscript.objects.all():
        manuscript.text_direction = TextDirection.RIGHT_TO_LEFT
        manuscript.save()
