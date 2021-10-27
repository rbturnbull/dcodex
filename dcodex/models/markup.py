from django.db import models

from polymorphic.models import PolymorphicModel

from bs4 import BeautifulSoup
import re
import regex


def remove_markup(string):
    string = re.sub("\[.*?\]", "", string)
    string = re.sub("\{.*?\}", "", string)
    string = string.replace("؟", "")

    string = BeautifulSoup(string, "lxml").text
    #    string = string.decode('utf8')

    return string


def get_punctuation_markers():
    punctuation = [
        "❊",
        "◦",
        "❇︎",
        "※",
        "ᐥ",
        "܀",
        "🕂",
        "⦿",
        ".",
        "?",
        "/",
        "؟",
        ",",
        "\\",
        "،",
        "∴",
        ":",
    ]
    return punctuation


def remove_punctuation(string):
    punctuation = get_punctuation_markers()
    for c in punctuation:
        string = string.replace(c, "")
    return string


def normalize_transcription(transcription):
    string = transcription + " "

    string = remove_punctuation(string)
    string = remove_markup(string)

    return string.strip()


class Markup(PolymorphicModel):
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="A descriptive name for this markup object.",
    )

    def __str__(self):
        return self.name

    def regularize(self, string):
        return normalize_transcription(string)

    def remove_markup(self, string):
        return remove_markup(string)

    def tokenize(self, string):
        string = self.remove_markup(string)
        string = string.replace(".", " .")
        string = string.replace(":", " :")
        string = string.replace(",", " ,")
        string = re.sub("\s+", " ", string)

        return string.split()

    def latex(self, string):
        string = string.replace("\\", "\\\\")
        string = re.sub("\{(.*?)\}", r"\\footnote{i.e. \1}", string)
        string = re.sub("\[(.*?)\]", r"\\footnote{\1}", string)

        # string = string.replace('؟','')
        string = self.latex_punctuation(string)

        string = BeautifulSoup(string, "lxml").text
        return string

    def tei(self, string):
        return string


class MinimalMarkup(Markup):
    def remove_markup(self, string):
        return string

    def regularize(self, string):
        return string


class StandardMarkup(Markup):
    pass


class SimpleArabicMarkup(Markup):
    def remove_arabic_vocalization(self, string):
        string = string.replace("ء", "")
        string = string.replace("إ", "ا")
        string = string.replace("آ", "ا")
        string = string.replace("أ", "ا")
        string = string.replace("ئ", "ا")
        string = string.replace("ً", "ا")
        string = string.replace("ٍ", "ا")
        string = string.replace("ؤ", "و")

        string = string.replace("ُ", "")
        string = string.replace("ً", "")
        string = string.replace("َ", "")
        string = string.replace("ِ", "")
        string = string.replace("ً", "")
        string = string.replace("ٍ", "")
        string = string.replace("ْ", "")
        string = string.replace("ٌ", "")
        string = string.replace("⧙", "")
        string = string.replace("ـ", "")
        string = string.replace("ّ", "")

        return string

    def standardise_arabic_graphemes(self, string):
        string = string + " "
        string = string.replace("ة", "ه")
        string = string.replace("ي ", "ا ")
        string = string.replace("ى ", "ا ")
        string = re.sub("\s\s+", " ", string)
        return string.strip()

    def regularize(self, string):
        string = string + " "

        string = self.remove_arabic_vocalization(string)
        string = remove_punctuation(string)
        string = remove_markup(string)
        string = self.standardise_arabic_graphemes(string)

        return string.strip()

    def latex(self, string):
        string = re.sub("\[.*?\]", "", string)
        string = re.sub("\{.*?\}", "", string)
        # string = string.replace('؟','')

        string = BeautifulSoup(string, "lxml").text
        string = self.latex_punctuation(string)

        if string == "":
            string = "\\textenglish{[Empty]}"
        return string

    def latex_with_markup(self, string):
        string = BeautifulSoup(string, "lxml").text
        string = string.replace("\\", "\\\\")

        string = re.sub("\{(.*?)\}", r"≾\1≿", string)

        string = regex.sub(
            r"(([\p{IsLatin}\d\:\,\–\-\.]+\s*)+)", r"\\textenglish{\1}", string
        )
        string = string.replace(" }", "} ")
        string = re.sub("\[(.*?)\]", r"\\footnote{\1}", string)
        string = re.sub(r"≾(.*?)≿", r"\\footnote{i.e. \1}", string)
        # string = re.sub('\{(.*?)\}', r'\\footnote{i.e. \1}', string);
        # string = re.sub('\{(.*?)\}', r'\\footnote{i.e. \1}', string)

        # string = string.replace('؟','')
        string = self.latex_punctuation(string)

        if string.startswith("\\footnote"):
            string = "\\textenglish{[See footnote.]}" + string

        return string

    def latex_punctuation(self, string):
        string = string.replace("ᐥ", "//")
        string = re.sub(r"[❊◦❇︎※܀]", r" $\\bigodot$ ", string)
        string = re.sub(r"\s+", r" ", string)
        string = string.replace("⧙", "$\\underbracket{\\ \\ }$")
        string = re.sub(r"\.\.\.+", r"$\\underbracket{\\ \\ \\ \\ \\ \\ }$", string)
        string = string.strip()
        return string

    def tei(self, string):
        string = BeautifulSoup(
            string, "lxml"
        ).text  # Hack: Remove TEI markup in text already

        string = re.sub("\[(.*?)\]", r'<note type="editorial">\1</note>', string)
        string = re.sub("\{(.*?)\}", r'<note type="editorial">i.e. \1</note>', string)
        string = re.sub("؟+", r'<note type="editorial">Uncertain</note>', string)
        string = re.sub(r"\.\.\.+", r"<gap />", string)
        for match in reversed(list(re.finditer("⧙+", string))):
            start, stop = match.span()
            extent = stop - start
            string = (
                string[:start]
                + f'<gap unit="char" extent="{extent}" />'
                + string[stop:]
            )
        string = re.sub(r"\.\.\.+", r"<gap />", string)
        return string
