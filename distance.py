from dcodex.models import *
import numpy as np
import pandas as pd
import Levenshtein
from collections import Counter
from matplotlib import pyplot as plt
import scipy.spatial.distance as ssd
import scipy.cluster.hierarchy as hcluster

def distance_matrix( manuscripts, verses, distance_func = Levenshtein.distance, verbose = False, triangular = False ):
    manuscripts_count = len(manuscripts)
    
    
    # Build dictionary of transcriptions to read from quickly
    transcriptions = {}
    counts = Counter()
    for ms_index, ms in enumerate(manuscripts):
        ms_transcriptions = {}
        for verse_index, verse in enumerate(verses):
            transcription = ms.transcription( verse )
            if transcription:
                counts.update([ms_index])
            ms_transcriptions[verse_index] = transcription.transcription if transcription else None
        transcriptions[ms_index] = ms_transcriptions
            
    matrix = np.zeros( (manuscripts_count,manuscripts_count), dtype=int )
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
                
                distance = distance_func( x_transcription, y_transcription )
                matrix[x_i][y_i] += distance

    if not triangular:
        for x_i in range(manuscripts_count):
            for y_i in range(x_i + 1, manuscripts_count):
                    matrix[y_i][x_i] = matrix[x_i][y_i]
    return matrix


def distance_matrix_dataframe( manuscripts, verses, distance_func = Levenshtein.distance, verbose = False, triangular = False ):
    np_matrix = distance_matrix( manuscripts, verses, distance_func, triangular )
    sigla = [ms.short_name() for ms in manuscripts]
    df = pd.DataFrame(data=np_matrix, index=sigla, columns=sigla)
    return df

def distance_matrix_csv( filename, manuscripts, verses, distance_func = Levenshtein.distance, verbose = False, triangular = False, sep='\t' ):
    df = distance_matrix_dataframe( manuscripts, verses, distance_func, triangular )
    df.to_csv(filename, sep=sep)
    return df


def dendrogram_from_distance_matrix( filename, np_matrix, labels ):
    distance_vec = ssd.squareform(np_matrix)    # converts square symmetric distrance matrix to vector
    fig = plt.figure(figsize=(20, 25))

    linkage = hcluster.linkage(distance_vec)
    dendro  = hcluster.dendrogram(linkage, orientation='right', labels=labels)
    plt.show()

    fig.savefig(filename, bbox_inches='tight')
    
def dendrogram( filename, manuscripts, verses, distance_func = Levenshtein.distance, verbose = False ):
    np_matrix = distance_matrix( manuscripts, verses, distance_func, triangular=False )
    sigla = [ms.short_name() for ms in manuscripts]

    return dendrogram_from_distance_matrix( filename, np_matrix, sigla )
    
    

def clean_siglum(siglum):
    siglum = siglum.replace("-", "_")
    siglum = siglum.replace(".", "_")
    siglum = siglum.replace("(", "_")
    siglum = siglum.replace(")", "_")
    siglum = siglum.replace(",", "_")
    siglum = siglum.replace(" ", "_")
    return siglum
    
    
def distance_matrix_nexus( filename, manuscripts, verses, distance_func = Levenshtein.distance ):
    np_matrix = distance_matrix( manuscripts, verses, distance_func )
    sigla = [clean_siglum(ms.short_name()) for ms in manuscripts]

    with open(filename, 'w') as f:
        f.write("#NEXUS\n")
        f.write("Begin taxa;\n")
        f.write("	Dimensions ntax=%d;\n" % (len(manuscripts)) )
        f.write("	Taxlabels\n" )
        for row_i in range(len(manuscripts)):
            f.write("	%s\n" % sigla[row_i] )
        f.write("	;\n" )
        f.write("End;\n" )
        f.write("Begin distances;\n" )
        f.write("	Format triangle=lower labels nodiagonal;\n" )
        f.write("		Matrix\n" )
        for row_i in range(len(manuscripts)):
            f.write("%s               " % sigla[row_i] )
            for column_i in range(row_i):            
                f.write("%f         " % (np_matrix[row_i][column_i]))                    
            f.write("\n")
        f.write("	;\n" )
        f.write("End;\n" )
                

