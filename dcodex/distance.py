from dcodex.models import *
import numpy as np
import pandas as pd
from collections import Counter
import scipy.spatial.distance as ssd
import scipy.cluster.hierarchy as hcluster
from collections import defaultdict
import Levenshtein
from pyxdameraulevenshtein import damerau_levenshtein_distance

import difflib


def similarity_from_edit_distance(string1, string2, edit_distance):
    max_length = max(len(string1), len(string2))
    if max_length == 0:
        return 1.0
    return (max_length - edit_distance) / max_length * 100.0


def similarity_levenshtein(string1, string2):
    return similarity_from_edit_distance(
        string1, string2, Levenshtein.distance(string1, string2)
    )


def similarity_damerau_levenshtein(string1, string2):
    return similarity_from_edit_distance(
        string1, string2, damerau_levenshtein_distance(string1, string2)
    )


def similarity_ratcliff_obershelp(string1, string2):

    s1 = difflib.SequenceMatcher(None, string1, string2)
    s2 = difflib.SequenceMatcher(None, string2, string1)
    return (s1.ratio() + s2.ratio()) * 50.0


def similarity_jaro(string1, string2):
    return Levenshtein.jaro(string1, string2) * 100.0


def distance_matrix_from_transcriptions(
    transcriptions, distance_func=Levenshtein.distance
):
    names = list(transcriptions.keys())
    count = len(names)

    # Setup initial empty list for each pair
    distances = defaultdict(lambda: defaultdict(list))

    for x_index, x_name in enumerate(names):
        for verse_id, x_transcription in transcriptions[x_name].items():
            for y_index in range(x_index + 1, count):
                y_name = names[y_index]

                if verse_id not in transcriptions[y_name]:
                    continue

                y_transcription = transcriptions[y_name][verse_id]

                distance = distance_func(x_transcription, y_transcription)
                max_length = max(len(x_transcription), len(y_transcription))
                if max_length == 0:
                    normalized_distance = 0.0
                else:
                    normalized_distance = distance / max_length

                distances[x_index][y_index].append(normalized_distance)

    distance_matrix = np.zeros((count, count))
    variance_matrix = np.zeros((count, count))
    for x_index, x_name in enumerate(names):
        for y_index in range(x_index + 1, count):
            distance_array = np.asarray(distances[x_index][y_index])
            distance_matrix[x_index][y_index] = np.mean(distance_array)
            variance_matrix[x_index][y_index] = np.var(distance_array)

            distance_matrix[y_index][x_index] = distance_matrix[x_index][y_index]
            variance_matrix[y_index][x_index] = variance_matrix[x_index][y_index]
    return distance_matrix, variance_matrix


def distance_matrix_unnormalized(
    manuscripts,
    verses,
    distance_func=Levenshtein.distance,
    verbose=False,
    triangular=False,
):
    manuscripts_count = len(manuscripts)

    # Build dictionary of transcriptions to read from quickly
    transcriptions = {}
    counts = Counter()
    for ms_index, ms in enumerate(manuscripts):
        ms_transcriptions = {}
        for verse_index, verse in enumerate(verses):
            transcription = ms.transcription(verse)
            if transcription:
                counts.update([ms_index])
            ms_transcriptions[verse_index] = (
                transcription.transcription if transcription else None
            )
        transcriptions[ms_index] = ms_transcriptions

    matrix = np.zeros((manuscripts_count, manuscripts_count), dtype=int)
    for verse_index in range(len(verses)):
        for x_i in range(manuscripts_count):
            x_transcription = transcriptions[x_i][verse_index]
            if not x_transcription:
                continue
            if verbose:
                print("Verse:", verse, "MS x:", x_i)
            for y_i in range(x_i + 1, manuscripts_count):
                y_transcription = transcriptions[y_i][verse_index]
                if not y_transcription:
                    continue

                distance = distance_func(x_transcription, y_transcription)
                matrix[x_i][y_i] += distance

    if not triangular:
        for x_i in range(manuscripts_count):
            for y_i in range(x_i + 1, manuscripts_count):
                matrix[y_i][x_i] = matrix[x_i][y_i]
    return matrix


def distance_matrix_dataframe(
    manuscripts,
    verses,
    distance_func=Levenshtein.distance,
    verbose=False,
    triangular=False,
):
    np_matrix = distance_matrix(manuscripts, verses, distance_func, triangular)
    sigla = [ms.short_name() for ms in manuscripts]
    df = pd.DataFrame(data=np_matrix, index=sigla, columns=sigla)
    return df


def distance_matrix_csv(
    filename,
    manuscripts,
    verses,
    distance_func=Levenshtein.distance,
    verbose=False,
    triangular=False,
    sep="\t",
):
    df = distance_matrix_dataframe(manuscripts, verses, distance_func, triangular)
    df.to_csv(filename, sep=sep)
    return df


def dendrogram_from_distance_matrix(filename, np_matrix, labels):
    from matplotlib import pyplot as plt

    distance_vec = ssd.squareform(
        np_matrix
    )  # converts square symmetric distrance matrix to vector
    fig = plt.figure(figsize=(20, 25))

    linkage = hcluster.linkage(distance_vec)
    dendro = hcluster.dendrogram(linkage, orientation="right", labels=labels)
    plt.show()

    fig.savefig(filename, bbox_inches="tight")


def dendrogram(
    filename, manuscripts, verses, distance_func=Levenshtein.distance, verbose=False
):
    np_matrix = distance_matrix(manuscripts, verses, distance_func, triangular=False)
    sigla = [ms.short_name() for ms in manuscripts]

    return dendrogram_from_distance_matrix(filename, np_matrix, sigla)


def clean_siglum(siglum):
    # TODO Use Translate call
    siglum = siglum.replace("-", "_")
    siglum = siglum.replace(".", "_")
    siglum = siglum.replace("(", "_")
    siglum = siglum.replace(")", "_")
    siglum = siglum.replace(",", "_")
    siglum = siglum.replace(" ", "_")
    siglum = siglum.replace("+", "_plus")
    return siglum


def nexus_distance_matrix(filename, distance_matrix, sigla):
    with open(filename, "w") as f:
        f.write("#NEXUS\n")
        f.write("Begin taxa;\n")
        f.write("	Dimensions ntax=%d;\n" % (len(sigla)))
        f.write("	Taxlabels\n")
        for row_i in range(len(sigla)):
            f.write("	%s\n" % clean_siglum(sigla[row_i]))
        f.write("	;\n")
        f.write("End;\n")
        f.write("Begin distances;\n")
        f.write("	Format triangle=lower labels nodiagonal;\n")
        f.write("		Matrix\n")
        for row_i in range(len(sigla)):
            f.write("%s               " % clean_siglum(sigla[row_i]))
            for column_i in range(row_i):
                f.write("%f         " % (distance_matrix[row_i][column_i]))
            f.write("\n")
        f.write("	;\n")
        f.write("End;\n")


def revbayes_distance_matrix(filename, distance_matrix, sigla):
    sigla_cleaned = [clean_siglum(siglum) for siglum in sigla]
    with open(filename, "w") as f:
        d = " "
        f.write("%s\n" % d.join(sigla_cleaned))

        for index, siglum in enumerate(sigla_cleaned):
            distances = d.join(
                [
                    str(distance_matrix[index][x] * 1000.0)
                    for x in range(len(distance_matrix[index]))
                ]
            )
            f.write("%s%s%s\n" % (siglum, d, distances))


def nexus_distance_matrix_from_transcriptions(filename, transcriptions, **kwargs):
    distance_matrix, _ = distance_matrix_from_transcriptions(transcriptions, **kwargs)
    sigla = list(transcriptions.keys())

    return nexus_distance_matrix(filename, distance_matrix, sigla)


def revbayes_distance_matrix_from_transcriptions(
    distance_filename, variance_filename, transcriptions, **kwargs
):
    distance_matrix, variance_matrix = distance_matrix_from_transcriptions(
        transcriptions, **kwargs
    )
    sigla = list(transcriptions.keys())

    revbayes_distance_matrix(distance_filename, distance_matrix, sigla)
    revbayes_distance_matrix(variance_filename, variance_matrix, sigla)
