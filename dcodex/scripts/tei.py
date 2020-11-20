from dcodex.models import Manuscript

def run(*args):
    if len(args) == 0:
        print("Please give a manuscript siglum.")
        return
    siglum = args[0]
    manuscript = Manuscript.find(siglum)
    if manuscript is None:
        print(f"Cannot understand manuscript siglum '{siglum}.")
        return 

    print(manuscript.tei_string())