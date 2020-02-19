import xml.etree.ElementTree as ET
import re

def remove_markup( string ):
    string = re.sub('\[.*?\]', '', string);
    string = re.sub('\{.*?\}', '', string);
    string = string.replace('؟','')

    tree = ET.fromstring("<xml>"+string+"</xml>");
#		root = tree.getroot()
#		print("tree text", tree.text)
#		print("tree tail", tree.tail)		
    for child in tree:
#			print("child text", child.text)
#			print("child tail", child.tail)
        if child.tag == "add" or child.tag == "del":
#				print("ADD")
            child.text = ''
            #tree.remove(child)

    
    string = ET.tostring(tree, encoding='utf8', method='text')
    string = string.decode('utf8')

    return string

def get_punctuation_markers():
    punctuation = ["❊", "◦", "❇︎", "※", "ᐥ", "܀", "🕂", "⦿", ".", "?", "/", "؟", ",", '\\', '،', '∴']
    return punctuation

def standardise_arabic_graphemes( string ):
    string = string + " ";
    string = string.replace('ة','ه')
    string = string.replace('ي ','ا ')
    string = string.replace('ى ','ا ')
    string = re.sub('\s\s+', ' ', string);		
    return string.strip()

def remove_punctuation( string ):
    punctuation = get_punctuation_markers()
    for c in punctuation:
        string = string.replace(c,'')
    return string

def remove_arabic_vocalization( string ):
    string = string.replace('ء','')
    string = string.replace('إ','ا')
    string = string.replace('آ','ا')
    string = string.replace('أ','ا')
    string = string.replace('ً','ا')
    string = string.replace('ٍ','ا')
    string = string.replace('ؤ','و')
    
    string = string.replace('ُ','')
    string = string.replace('َ','')
    string = string.replace('ِ','')
    string = string.replace('ً','')
    string = string.replace('ٍ','')
    string = string.replace('ْ','')
    string = string.replace('ٌ','')
    return string


def normalize_transcription( transcription ):
    string = transcription + " ";

    string = remove_arabic_vocalization( string )
    string = remove_punctuation( string )
    try:
        string = remove_markup( string )
    except:
        pass
    string = standardise_arabic_graphemes( string )

    return string.strip()
