
from django.db import models

from polymorphic.models import PolymorphicModel

from bs4 import BeautifulSoup
import re
import regex

def remove_markup( string ):
    string = re.sub('\[.*?\]', '', string);
    string = re.sub('\{.*?\}', '', string);
    string = string.replace('؟','')

    string = BeautifulSoup(string, "lxml").text
#    string = string.decode('utf8')

    return string

def get_punctuation_markers():
    punctuation = ["❊", "◦", "❇︎", "※", "ᐥ", "܀", "🕂", "⦿", ".", "?", "/", "؟", ",", '\\', '،', '∴', ':']
    return punctuation

def remove_punctuation( string ):
    punctuation = get_punctuation_markers()
    for c in punctuation:
        string = string.replace(c,'')
    return string



def normalize_transcription( transcription ):
    string = transcription + " "

    string = remove_punctuation( string )
    string = remove_markup( string )    

    return string.strip()

class Markup(PolymorphicModel):
    name = models.CharField(max_length=255, blank=True, help_text='A descriptive name for this markup object.')

    def __str__(self):
        return self.name

    def regularize( self, string ):
        return normalize_transcription( string )

    def remove_markup(self, string):
        return remove_markup( string )

    def tokenize( self, string ):
        string = self.remove_markup(string)
        string = string.replace("."," .")
        string = string.replace(":"," :")
        string = string.replace(","," ,")
        string = re.sub("\s+"," ", string)

        return string.split()

    def latex(self, string):
        string = string.replace("\\", "\\\\")
        string = re.sub('\{(.*?)\}', r'\\footnote{i.e. \1}', string);
        string = re.sub('\[(.*?)\]', r'\\footnote{\1}', string);

        # string = string.replace('؟','')
        string = string.replace("ᐥ", "//")
        

        
        string = re.sub(r'[❊◦❇︎※܀]', r'$\\bigodot$', string)

        string = BeautifulSoup(string, "lxml").text
        return string


class StandardMarkup(Markup):
    pass



################### Arabic ###################

def remove_arabic_vocalization( string ):
    string = string.replace('ء','')
    string = string.replace('إ','ا')
    string = string.replace('آ','ا')
    string = string.replace('أ','ا')
    string = string.replace('ئ','ا')
    string = string.replace('ً','ا')
    string = string.replace('ٍ','ا')
    string = string.replace('ؤ','و')
    
    string = string.replace('ُ','')
    string = string.replace('ً','')
    string = string.replace('َ','')
    string = string.replace('ِ','')
    string = string.replace('ً','')
    string = string.replace('ٍ','')
    string = string.replace('ْ','')
    string = string.replace('ٌ','')
    string = string.replace('⧙','')
    string = string.replace('ـ','')
    string = string.replace('ّ','')    
    
    return string


def standardise_arabic_graphemes( string ):
    string = string + " "
    string = string.replace('ة','ه')
    string = string.replace('ي ','ا ')
    string = string.replace('ى ','ا ')
    string = re.sub('\s\s+', ' ', string);		
    return string.strip()


class SimpleArabicMarkup(Markup):

    def regularize(self, string):
        string = transcription + " "

        string = self.remove_arabic_vocalization( string )
        string = remove_punctuation( string )
        string = remove_markup( string )    
        string = standardise_arabic_graphemes( string )

        return string.strip()

    def latex(self, string):
        string = BeautifulSoup(string, "lxml").text
        string = string.replace("\\", "\\\\")

        string = re.sub('\{(.*?)\}', r'≾\1≿', string)

        string = regex.sub(r"(([\p{IsLatin}\d\:\,\–\-\.]+\s*)+)", r"\\textenglish{\1}", string)
        string = string.replace(" }", "} ")
        string = re.sub('\[(.*?)\]', r'\\footnote{\1}', string);

        # string = string.replace('؟','')
        string = string.replace("ᐥ", "//")
        
        # string = re.sub('\{(.*?)\}', r'\\footnote{i.e. \1}', string);
        # string = re.sub('\{(.*?)\}', r'\\footnote{i.e. \1}', string)
        
        string = re.sub(r'≾(.*?)≿', r' $\\bigodot$ ', string)
        string = re.sub(r'\s+', r' ', string)

        string = string.strip()
        if string.startswith( "\\footnote" ):
            string = "\\textenglish{[See footnote.]}" + string

        return string
