from django.db import models
from django.conf import settings
from polymorphic.models import PolymorphicModel
from django.shortcuts import render
import re
from django.db.models import Max, Min
import os
import glob
import logging
import pandas as pd
import numpy as np
import gotoh_counts
from .strings import normalize_transcription
from .distance import similarity_levenshtein, similarity_damerau_levenshtein, similarity_ratcliff_obershelp, similarity_jaro
from scipy.special import expit

def facsimile_dir():
    return settings.MEDIA_ROOT


class TextDirection(models.TextChoices):
    RIGHT_TO_LEFT = 'R'
    LEFT_TO_RIGHT = 'L'


class Markup(PolymorphicModel):
    name = models.CharField(max_length=255, blank=True, help_text='A descriptive name for this markup object.')

    def __str__(self):
        return self.name

    def regularise( self, string ):
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


class StandardMarkup(Markup):
    pass


# Create your models here.
class Manuscript(PolymorphicModel):
    """ 
    An abstract class used for bringing together all the elements of a document. 
    """
    name = models.CharField(max_length=200, blank=True, help_text='A descriptive name for this manuscript.')
    siglum = models.CharField(max_length=20, blank=True, help_text='A unique short string for this manuscript.')
    markup = models.ForeignKey(Markup, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None, help_text='The default markup class for this manuscript.')
    text_direction = models.CharField(max_length=1, choices=TextDirection.choices, default=TextDirection.LEFT_TO_RIGHT )

    def __str__(self):
        if self.name and self.siglum:
            if self.name == self.siglum:
                return self.siglum
            return "%s: %s" % (self.siglum, self.name)
        if self.name:
            return self.name
        if self.siglum:
            return self.siglum
        return str(self.id)
    def short_name(self):
        if self.siglum:
            return self.siglum
        if self.name:
            return self.name
        return str(self.id)
    class Meta:
        ordering = ['siglum', 'name']
        
    @classmethod
    def verse_class(cls):
        return Verse

    @classmethod
    def transcription_class(cls):
        return VerseTranscription

    @classmethod
    def verse_from_string(cls, verse_as_string):
        return cls.verse_class().get_from_string( verse_as_string )

    @classmethod
    def verse_from_id(cls, verse_id):
        return cls.verse_class().objects.filter(id=verse_id).first()        
        
    @classmethod
    def verse_from_dict(cls, dictionary):
        return cls.verse_class().get_from_dict( dictionary )

    @classmethod
    def find(cls, description):
        manuscript = cls.objects.filter( siglum=description ).first()
        if manuscript:
            return manuscript
        return cls.objects.filter( name=description ).first()
        

    def verse_search_template(self):
        raise NotImplementedError("Please implement this method")

    def render_verse_search( self, request, verse ):
        return render(request, self.verse_search_template(), {'verse': verse, 'manuscript': self, 'next_verse':self.next_verse(verse), 'prev_verse':self.prev_verse(verse), } )
    
    def location_popup_template(self):
        raise NotImplementedError("Please implement this method")
    
    def render_location_popup( self, request, verse ):
        return render(request, self.location_popup_template(), {'verse': verse, 'manuscript': self,  'next_verse':self.next_verse(verse), 'prev_verse':self.prev_verse(verse), } )
        
    def transcription( self, verse ):
        return self.transcription_class().objects.filter( manuscript=self, verse=verse ).first()

    def normalized_transcription( self, verse ):
        transcription = self.transcription(verse)
        if transcription:
            return transcription.normalize()
        return None

    def comparison_texts( self, verse, manuscripts = None ):
        if manuscripts is None:
            return self.transcription_class().objects.filter( verse=verse ).all()        

        return self.transcription_class().objects.filter( verse=verse, manuscript__in=manuscripts ).all()                

    def save_transcription( self, verse, text ):
        try:
            transcription, created = self.transcription_class().objects.update_or_create(
                manuscript=self, 
                verse=verse, 
                defaults={"transcription": text}
            )
        except:
            self.transcription_class().objects.filter(manuscript=self, verse=verse).delete()
            return self.save_transcription( verse, text )

        return transcription

    def title_dict( self, verse ):
        ref = verse.reference_abbreviation()
        url_ref = verse.url_ref()
        dict = { 
            'title': "%s – %s" % (self.siglum, ref), 
            'url': "/dcodex/ms/%s/%s/" % ( self.siglum, url_ref ),
            'verse_url_ref': url_ref,             
        }
        return dict    

    def save_location( self, verse, pdf, page, x, y ):
        location, created = VerseLocation.objects.update_or_create(
            manuscript=self, 
            verse=verse, 
            defaults={"pdf": pdf, "page": page, 'x':x, 'y':y}
        )
        return location

    def transcriptions( self ):
        return self.transcription_class().objects.filter( manuscript=self ).order_by( 'verse__rank' )
                
    def verse_ids_with_locations(self):
        # See https://docs.djangoproject.com/en/3.0/ref/models/querysets/#values-list
        return VerseLocation.objects.filter( manuscript=self ).values_list('verse__id', flat=True)
        
    def normalized_transcriptions_dict( self ):
        return {transcription.id:transcription.normalize(  ) for transcription in self.transcriptions()}

    def transcriptions_range( self, ranges=None, range=None, start=None, end=None ):
        if ranges is None:
            if range is None:
                range = [start, end]
            ranges = [range]

        transcriptions = []
        for range in ranges:
            transcriptions_set = self.transcriptions()
            if range[0] is not None:
                transcriptions_set = transcriptions_set.filter( verse__id__gte = range[0].id )
            if range[1] is not None:
                transcriptions_set = transcriptions_set.filter( verse__id__lte = range[1].id )
            
            transcriptions += transcriptions_set.all()
            #print(  'range', range[0].id, range[1].id, len(transcriptions))
        
        return transcriptions
        
    def transcriptions_range_dict( self, **kwargs ):
        return { transcription.verse.id : transcription.transcription for transcription in self.transcriptions_range( **kwargs ) }
    
    def location_before_or_equal( self, verse ):
        try:
            return VerseLocation.objects.filter( manuscript=self, verse__id__lte=verse.id ).order_by('-verse__id').first()
        except:
            return VerseLocation.objects.filter( manuscript=self ).order_by('-verse__id').first()                    
        
    def location_after( self, verse ):
        return VerseLocation.objects.filter( manuscript=self, verse__id__gt=verse.id ).order_by('verse__id').first()
        
    def last_location( self, pdf ):
        return VerseLocation.objects.filter( manuscript=self, pdf=pdf ).order_by('-verse__id').first()
    def first_location( self, pdf ):
        return VerseLocation.objects.filter( manuscript=self, pdf=pdf ).order_by('verse__id').first()
        
    def location_above( self, pdf, page, y ):
        # Search on this page
        location = VerseLocation.objects.filter( manuscript=self, pdf=pdf, page=page, y__lte=y ).order_by('-y').first()
        if location:
            return location
        # Search on previous pages
        location = VerseLocation.objects.filter( manuscript=self, pdf=pdf, page__lt=page ).order_by('-page','-y').first()
        return location

    def location_below( self, pdf, page, y ):
        # Search on this page
        location = VerseLocation.objects.filter( manuscript=self, pdf=pdf, page=page, y__gte=y ).order_by('y').first()
        if location:
            return location
        # Search on previous pages
        location = VerseLocation.objects.filter( manuscript=self, pdf=pdf, page__gt=page ).order_by('page','y').first()
        return location

        
    def gotoh_counts_verses( self, ms, verses, gotoh_param=(0,-1,-1,-1) ):
        total_counts = np.zeros( (4,) )
        for verse in verses:            
            transcription1 = self.normalized_transcription(verse)
            transcription2 = ms.normalized_transcription(verse)
            if transcription1 and transcription2:
                counts = gotoh_counts.counts( transcription1, transcription2, *gotoh_param )
                print(verse, counts)
                total_counts += np.asarray( counts )
        return total_counts

    def compare_transcriptions( self, weights, prior_log_odds=0.0, **kwargs ):
        counts = self.gotoh_counts_verses( **kwargs )
        length = counts.sum()
        similarity = counts[0]/length*100.0 if length > 0 else np.NAN
        logodds = prior_log_odds + np.dot( counts, weights )
        prob = expit( logodds )
        return similarity, prob, logodds
                       
    def gotoh_counts( self, mss=None, transcriptions=None, gotoh_param=(0,-1,-1,-1) ):
        if transcriptions is None:
            transcriptions = self.transcriptions()
        if mss is None:
            print("You need to specify the manuscripts ('mss') to compare with.")
            raise KeyError
            
        columns = ['verse__id', 'verse__rank', 'verse_description']
        for ms in mss:
            columns += [ms.siglum+"_m", ms.siglum+"_d", ms.siglum+"_g",ms.siglum+"_e" ]
        df = pd.DataFrame( columns=columns )
        for transcription in transcriptions:
            row = {'verse__id':transcription.verse.id, 'verse__rank':transcription.verse.rank, 'verse_description':str(transcription.verse) }
            normalized_transcription = transcription.normalize()
            for ms in mss:
                ms_transcription = ms.transcription( transcription.verse )
                if ms_transcription:
                    counts = gotoh_counts.counts( normalized_transcription, ms_transcription.normalize(), *gotoh_param )
                else:
                    counts = (0,0,0,0)
                row[ms.siglum+"_m"] = counts[0]
                row[ms.siglum+"_d"] = counts[1]
                row[ms.siglum+"_g"] = counts[2]
                row[ms.siglum+"_e"] = counts[3]
                
            df = df.append(row, ignore_index=True)
                    
        return df

    def rolling_average_gotoh_counts( self, window=4, **kwargs ):
        df = self.gotoh_counts( **kwargs )        
        columns = df.columns
        
        def average_over_window( row ):
            rank = row['verse__rank']            
            window_df = df[ (df['verse__rank'] >= rank - window) & (df['verse__rank'] <= rank + window) ]
            values = [row[x] for x in columns[:3]] + [window_df[x].sum() for x in columns[3:]]
            return pd.Series( values, columns )
            
        return df.apply( average_over_window, axis=1 )
        
    def rolling_average_probability( self, weights, mss, prior_log_odds=0.0, **kwargs ):
        weights = np.asarray( weights )    
        df = self.rolling_average_gotoh_counts( mss=mss, **kwargs )
        
        columns = list(df.columns[:3])
        for ms in mss:
            columns += [ms.siglum+"_length", ms.siglum+"_similarity", ms.siglum+"_logodds", ms.siglum+"_probability" ]
        
        def compute_posterior( row ):
            values = [row[x] for x in columns[:3]]
            for ms in mss:
                counts = np.asarray( [row[ms.siglum+"_m"], row[ms.siglum+"_d"], row[ms.siglum+"_g"], row[ms.siglum+"_e"]] )
                length = counts.sum()
                similarity = counts[0]/length*100.0 if length > 0 else np.NAN
                logodds = prior_log_odds + np.dot( counts, weights )
                prob = expit( logodds )
                values += [length, similarity, logodds, prob]
            return pd.Series( values, columns )
        
        return df.apply( compute_posterior, axis=1 )

    def text_direction_css(self):
        """ The CSS class for text from this manuscript to express the direction. """
        return "ltr" if self.text_direction == "L" else "rtl"

    def location( self, verse, verbose=True ):
        """ Finds (or estimates) the location of a verse in a manuscript.
        
        If the location is already tagged in the manuscript, the saved location is returned from the database. 
        If not, then it estimates the location of the verse via interpolation or extrapolation 
        """
        
        if not verse:
            return VerseLocation.objects.filter( manuscript=self ).order_by('-verse__id').first()                    
            
        location_A = self.location_before_or_equal( verse )
        
        # If this location is already saved then return it
        if location_A and verse.id == location_A.verse.id:
            return location_A

        # Find two locations to interpolate from
        if location_A is None:
            location_A = self.location_after( verse )
            if location_A is None: 
                # No verses have been transcribed, then nothing is known about locations in the manuscript and so return nothing
                return None

            location_B = self.last_location( pdf=location_A.pdf )
            if location_B is None or location_B.id == location_A.id:
                return location_A
        else:
            location_B = self.location_after( verse )
            if location_B is None:
                location_B = location_A;
                location_A = self.first_location( location_B.pdf )
                if location_A is None or location_A.id == location_B.id:
                    return location_B
    
        if location_A.pdf != location_B.pdf: # Hack for different PDFs. This out to be fixed
            return location_A
    
        textbox_top = VerseLocation.textbox_top(self)

        location_A_value = location_A.value( textbox_top ) 
        location_B_value = location_B.value( textbox_top ) 

        distance_verse_location_A = self.distance_between_verses( location_A.verse, verse )
        distance_locations_B_location_A = self.distance_between_verses( location_A.verse, location_B.verse )

        if distance_locations_B_location_A == 0:
            return location_A
        value_delta = (distance_verse_location_A)*(location_B_value - location_A_value)/(distance_locations_B_location_A)
    
        my_location_value = location_A_value + value_delta
        page = int(my_location_value)
        y = (my_location_value - page) * (1.0-2*textbox_top) + textbox_top
        
        
        if verbose:
            logger = logging.getLogger(__name__)            
            logger.error( "Location A: %s " % str(location_A) )
            logger.error( "Location B: %s " % str(location_B) )
            logger.error( "distance_verse_location_A: %s " % str(distance_verse_location_A) )
            logger.error( "distance_locations_B_location_A: %s " % str(distance_locations_B_location_A) )
        
        
        return VerseLocation(manuscript=self, pdf=location_A.pdf, verse=verse, page=page, y=y, x=0.0)
    def next_verse(self, verse):
        """ Returns the next verse after the specified verse in this manuscript. """
        return verse.next()

    def prev_verse(self, verse):
        """ Returns the next verse after the specified verse in this manuscript. """    
        return verse.prev()
    
    def distance_between_verses( self, verse1, verse2 ):
        return verse1.distance_to(verse2)



    def approximate_verse_at_position( self, pdf, page, x, y ):
        """ Estimates the verse at a particular location """
        location_A = self.location_above( pdf, page, y )
        
        # Find two locations to interpolate from
        if location_A is None:
            location_A = self.location_below( pdf, page, y )
            if location_A is None: 
                # No verses have been transcribed, then nothing is known about locations in the manuscript and so return nothing
                return None

            location_B = self.last_location( pdf=location_A.pdf )
            if location_B is None or location_B.id == location_A.id:
                return location_A
        else:
            location_B = self.location_below( pdf, page, y )
            if location_B is None:
                location_B = location_A;
                location_A = self.first_location( location_B.pdf )
                if location_A is None or location_A.id == location_B.id:
                    return location_B
    
        if location_A.pdf != location_B.pdf: # Hack for different PDFs. This out to be fixed
            return location_A

        textbox_top = VerseLocation.textbox_top(self)

        location_A_value = location_A.value( textbox_top ) 
        location_B_value = location_B.value( textbox_top ) 
        
        target_value = page + ( y - textbox_top )/(1.0-2*textbox_top)
        
        additional_mass = self.distance_between_verses( location_A.verse, location_B.verse ) * (target_value - location_A_value)/(location_B_value - location_A_value)
        return self.verse_from_mass_difference( location_A.verse, additional_mass )
        
    def verse_from_mass_difference( self, reference_verse, additional_mass ):
        """Default implementation assuming mass of each verse = 1 and that the verses are ordered according to the verse id"""
        verse_id = reference_verse.id + int(additional_mass)
        return self.verse_class().objects.filter( id=verse_id ).first()
                
    def family_ids_at( self, verse ):
        """ Returns a set of family ids which are affiliated with this manuscript at this verse. """
        family_ids = set()
        checked_family_ids=set() 
        
        for affiliation in self.affiliationbase_set.all():
            families = affiliation.families_at(verse)
            for family in families:
                family_ids.add( family.id )
                if family.id not in checked_family_ids:
                    family_ids.update( family.afilliated_family_ids_at(verse, checked_family_ids) )
        return family_ids
        
    def families_at(self, verse):
        return FamilyBase.objects.filter(id__in=self.family_ids_at(verse))

    def is_in_family_at(self, family, verse):
        ids = self.family_ids_at(verse)
        return family.id in ids 
        

class ManuscriptImage():
    page = None
    folio = None
    src = None
    def __init__(self, page, src, folio=None):
        self.page = page
        self.src = src
        self.folio = folio
    def __hash__(self):
        return hash((self.page, self.src, self.folio))
    
# TODO Refactor as 'Facsimile' class and add 'PDFFacsimile' class using qpdf and ImageMagick.
class PDF(models.Model):
    filename = models.CharField(max_length=200)
    page_count = models.IntegerField(blank=True, null=True, default=None)
    
    first_side_names  = ['r','a','ا']
    second_side_names = ['v','b','ب']

    def __str__(self):
        return self.filename
    class Meta:
        verbose_name_plural = 'PDFs'
        

    
    def get_page_count(self):
        logger = logging.getLogger(__name__)    
        
        if self.page_count:
            return self.page_count

        dir = facsimile_dir()
        glob_string = "%s/facsimiles/%s-*.jpg" % (dir, self.filename)
        files = glob.glob(glob_string)
        logger.error(glob_string)
        logger.error(files)


        page_count = 0
        for file in files:
            m = re.match(".*-([\d]+).jpg", file)
            if m:
                page_index = int(m.group(1))
                if page_index > page_count:
                    page_count = page_index
        if page_count == 0:
            return 0
        self.page_count = page_count
        if self.id:
            self.save()
        return self.page_count
    
    def closest_prev_page( self, page_index ):
        return Page.objects.filter( pdf=self, page__lte=page_index ).order_by('-page').first()
    def closest_prev_folio( self, folio_number ):
        return Page.objects.filter( pdf=self, folio__lte=folio_number ).order_by('-folio').first()
    
    def folio_name( self, page_index ):
        prev_page = self.closest_prev_page( page_index )
        if not prev_page:
            return ""
        
        x = prev_page.folio * 2 - 1
        name_index = 0
        
        if prev_page.side in self.second_side_names:
            x += 1
            name_index = self.second_side_names.index(prev_page.side)
        elif prev_page.side in self.first_side_names:
            name_index = self.first_side_names.index(prev_page.side)
        
        y = page_index - prev_page.page + x
        
        folio_side = self.first_side_names[name_index] if y % 2 == 1 else  self.second_side_names[name_index]

        folio_number = (int)((y+1)/2)
        return "%d%s" % (folio_number, folio_side)
        
    def page_number( self, folio_ref ):
        if folio_ref.isdigit():
            return int( folio_ref )
        
        # Come up with possible names for sides to search for
        possible_side_names = "".join( self.first_side_names + self.second_side_names )
        
        # Search for folio number and side
        m = re.match( "([0-9]*)([%s])" % (possible_side_names), folio_ref )
        if m:
            folio_number = int(m.group(1))
            folio_side   = m.group(2)

            prev_folio = self.closest_prev_folio( folio_number )
            if not prev_folio:
                return folio_number
            
            x = prev_folio.folio * 2 - 1
            if prev_folio.side in self.second_side_names:
                x += 1

            y = folio_number * 2 - 1        
            if folio_side in self.second_side_names:
                y += 1
            
            return prev_folio.page + y - x
            
        return None



    
    
    def thumbnails(self):
        page_count = self.get_page_count()
        thumbnails = []
        for page_index in range(1, page_count + 1):
            folio = self.folio_name( page_index )
            thumbnails.append( ManuscriptImage( page_index, self.thumbnail_path(page_index), folio ) )
        return thumbnails

    def images(self):
        page_count = self.get_page_count()
        thumbnails = []
        for page_index in range(1, page_count + 1):
            folio = self.folio_name( page_index )
            thumbnails.append( ManuscriptImage( page_index, self.image_path(page_index), folio ) )
        return thumbnails

    def thumbnail_path(self, page_index):
        src = "facsimiles/small/%s-%d.small.jpg" % (self.filename, page_index)
        dir = facsimile_dir()      
        
        system_path = "%s/%s" % (dir, src)
                  
        if not os.access(system_path, os.R_OK):
            src = self.image_path(page_index)
        return src

    def image_path(self, page_index):
        return "facsimiles/%s-%d.jpg" % (self.filename, page_index)

class Page(models.Model):
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE) # SHOULD THIS BE HERE??
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    page = models.IntegerField()
    folio = models.IntegerField()
    side = models.CharField(max_length=20)
    def __str__(self):
        return "%s %d%s (%s p%d)" % (self.manuscript.short_name(), self.folio, self.side, self.pdf.__str__(), self.page )
    
    
    
    
    
    
    
class Verse(PolymorphicModel):
    """ An abstract class used for the smallest textual unit appropriate for the manuscript type. 
    Each Verse object ought only occur once per manuscript. 
    For each possible verse, there must be an instance of a child-class of Verse saved in the database. 
    """

    rank = models.IntegerField(help_text="An integer to enable sorting of the verses (deprecated)") # Is this necessary??
    
    
    def __str__(self):
        return self.reference()
    
    def reference(self, abbreviation = False, end_verse=None):
        """ Returns a unique reference for this verse as a string.
        
        :param abbreviation: If set to True, the method returns an abbreviated form of the reference (e.g. 'Mt 1:1'). Like the unabbreviated reference, this must be unique for this verse instance.
        :type abbreviation: Boolean
        :param abbreviation: If provided, the method returns the reference as a range between 'self' and 'end_verse'
        :type abbreviation: `dcodex.Verse`
        :return: The reference string. For example 'Matthew 1:1'.
        :rtype: String
        """    
        if end_verse != None:
            return "%s–%s" % (self.reference( abbreviation=abbreviation ), end_verse.reference( abbreviation=abbreviation ) )
        return "%d" % (self.pk)
    def url_ref(self):
        """ Returns a unique reference for this verse as a string that is appropriate to use in a URL. The default implementation is to use the unabbreviated reference string and remove spaces."""
        return self.reference_abbreviation().replace(" ", '')

    def reference_abbreviation(self):
        """Returns the reference string with the abbreviation option set to True. 
        
        This is useful for Django templates where giving arguments to functions is not always simple
        """
        return self.reference(abbreviation = True)

    
    # Should this be here? This should be handled by the manuscript
    def next(self):
        """Deprecated.

        This should be handled by the Manuscript.
        """
        return self.__class__.objects.filter( rank__gt=self.rank ).order_by('rank').first()

    # Should this be here? This should be handled by the manuscript
    def prev(self):
        """Deprecated.

        This should be handled by the Manuscript.
        """
        return self.__class__.objects.filter( rank__lt=self.rank ).order_by('-rank').first()

    # Should this be here? This should be handled by the manuscript
    def cumulative_mass(self):
        """Deprecated.

        This should be handled by the Manuscript.
        """
        return self.rank

    # Should this be here? This should be handled by the manuscript        
    def distance_to(self, other_verse):
        """Deprecated.

        This should be handled by the Manuscript.
        """
        return other_verse.cumulative_mass() - self.cumulative_mass()

    @classmethod
    def get_from_string( cls, verse_as_string ):
        """ Locates a `dcodex.Verse` object instance from a string.
        
        As a minimum this method must be able to interpret the unique reference string (with any abbreviation option if appropriate). This function is used to find verses embedded in a URL.
        
        :param verse_as_string: A reference string for the sought-after verse.
        :type verse_as_string: String
        :return: The verse associated with that string. If none exists, then it returns None.
        :rtype: `dcodex.Verse`
        """        
        return None

    @classmethod
    def get_range_from_strings( cls, verse_as_string1, verse_as_string2 ):
        """ Convenience function that returns a two-element list with the two verses associated with the two strings """
        return [cls.get_from_string( verse_as_string1 ), cls.get_from_string( verse_as_string2 ) ]

    @classmethod
    def get_from_dict( cls, dictionary ):
        """ Locates a `dcodex.Verse` object instance from a Python dictionary.
        
        The keys for the dictionary are determined by the child class.
        
        :param dictionary: A dictionary with elements used to find the `dcodex.Verse`.
        :type dictionary: Dictionary
        :return: The `dcodex.Verse` associated with that string. If none exists, then it returns None.
        :rtype: `dcodex.Verse`
        """            
        return None
        
        
        
        

    
class VerseLocation(models.Model):
    """The 'Location' class joins a manuscript and verse object and associates them with the pixel coordinates on a facsimile image."""
    
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE)
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    page = models.IntegerField()
    x = models.FloatField(help_text="The number of horizontal pixels from the left of the facsimile image to the the location of the verse, normalized by the height of the image.")
    y = models.FloatField(help_text="The number of vertical pixels from the top of the facsimile image to the the location of the verse, normalized by the height of the image.")
    def __str__(self):
        return "%s in %s in %s on p%d at (%0.1g, %0.1g)" % (self.verse.reference(abbreviation=True), self.manuscript.short_name(), self.pdf.__str__(), self.page, self.x, self.y )

    @classmethod
    def textbox_top(cls, manuscript):
        default = 0.2
        try:
            minimum = cls.objects.filter(manuscript=manuscript).aggregate( Min('y') )['y__min']
        except:
            return default

        if minimum < 0.001 or minimum > default:
            return default
        return minimum

    def value(self, textbox_top = None):
        if textbox_top == None:
            textbox_top = self.textbox_top(self.manuscript)
            
        return self.page + (self.y - textbox_top)/(1.0-2.0 * textbox_top)        
        
    def image_path(self):
        return self.pdf.image_path( self.page )
    def values_dict(self):
        return {'manuscript_id': self.manuscript.id, 'pdf_filename': self.pdf.filename, 'x':self.x, 'y':self.y, 'page':self.page, 'verse_id':self.verse.id, 'ref':self.verse.reference_abbreviation(), 'tooltip':'', 'exact': True if self.pk else False }
        

class VerseTranscriptionBase(PolymorphicModel):
    """The 'Transcription' class stores the text of a transcribed verse and associates it with the manuscript and verse instances."""
    
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE, help_text='The manuscript this transcription is from.' )
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE, help_text='The verse of this transcription.')
    transcription = models.CharField(max_length=1024, help_text='The unnormalized text of this transcription.') # This should be refactored as 'text' and made a TextField.
    markup = models.ForeignKey(Markup, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None, help_text='The markup class for this transcription.')
    
    def __str__(self):
        return "%s in %s: %s" % (self.verse.reference(abbreviation=True), self.manuscript.short_name(), self.transcription )

    def get_markup( self ):
        if self.markup:
            return self.markup
        
        if self.manuscript.markup:
            return self.manuscript.markup

        return None

    def normalize(self):
        markup = self.get_markup()
        if markup:
            return markup.regularize( self.transcription )
        
        return normalize_transcription( self.transcription )

    def tokenize(self):
        markup = self.get_markup()
        if markup:
            return markup.tokenize( self.transcription )
        
        return normalize_transcription( self.transcription ).split(" ")

    def similarity( self, comparison_transcription, similarity_func = None ):
        return similarity_func( self.normalize(), comparison_transcription.normalize() )

    def similarity_levenshtein( self, comparison_transcription ):
        return self.similarity( comparison_transcription, similarity_levenshtein )
    def similarity_damerau_levenshtein( self, comparison_transcription ):
        return self.similarity( comparison_transcription, similarity_damerau_levenshtein )
    def similarity_ratcliff_obershelp( self, comparison_transcription ):
        return self.similarity( comparison_transcription, similarity_ratcliff_obershelp )
    def similarity_jaro( self, comparison_transcription ):
        return self.similarity( comparison_transcription, similarity_jaro )
        
class VerseTranscription(VerseTranscriptionBase):
    def __str__(self):
        return super(VerseTranscription, self).__str__()
    
class FamilyBase(PolymorphicModel):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name    
                
    def manuscript_ids_at( self, verse, checked_family_ids=None ):
        """ Returns a set of manuscript ids which are affiliated with this family at this verse. """
        if checked_family_ids is None:
            checked_family_ids = set()
        checked_family_ids.add( self.id )
        manuscript_ids = set()
        for affiliation in self.affiliationbase_set.all():
            manuscript_ids.update( affiliation.manuscript_ids_at(verse) )
            families = affiliation.families_at(verse)
            for family in families:
                if family.id not in checked_family_ids:
                    manuscript_ids.update( family.manuscript_ids_at(verse, checked_family_ids) )
        return manuscript_ids


    def manuscript_and_verse_ids_at( self, verse, checked_family_ids=None ):
        """ Returns a set of manuscript and verse id pairs which are affiliated with this family at this verse. """
        if checked_family_ids is None:
            checked_family_ids = set()
        checked_family_ids.add( self.id )
        pairs = set()
        for affiliation in self.affiliationbase_set.all():
            pairs_for_affiliation = affiliation.manuscript_and_verse_ids_at(verse)
            pairs.update( pairs_for_affiliation )
            families = affiliation.families_at(verse)
            for family in families:
                if family.id not in checked_family_ids:
                    pairs.update( family.manuscript_and_verse_ids_at(verse, checked_family_ids) )
        
        return pairs
    
    def manuscripts_at(self, verse):
        """ Returns a Django query set for all the manuscripts with this fmaily at this verse. """    
        return Manuscript.objects.filter( id__in=self.manuscript_ids_at(verse) )


    def afilliated_family_ids_at( self, verse, checked_family_ids=None ):
        """ Returns a set of family ids which are affiliated with this family at this verse (including itself). """    
        if checked_family_ids is None:
            checked_family_ids = set()
        
        checked_family_ids.add( self.id )
        
        family_ids = {self.id}
        for affiliation in self.affiliationbase_set.all():
            families = affiliation.families_at(verse)
            for family in families:
                family_ids.add(family.id)
                if family.id not in checked_family_ids:
                    family_ids.update( family.afilliated_family_ids_at(verse, checked_family_ids) )
        return family_ids
        
    def add_manuscript_to_affiliation( self, affiliation, manuscript ):
        affiliation.save()
        affiliation.families.add( self )
        affiliation.manuscripts.add( manuscript )
        affiliation.save()        
        return affiliation
    
    def add_family_to_affiliation( self, affiliation, family ):
        affiliation.save()
        affiliation.families.add( self )
        affiliation.families.add( family )
        affiliation.save()        
        return affiliation
        
    def transcriptions_at( self, verse, manuscript_ids=None ):
        transcriptions = []
        for manuscript_id, verse_id in self.manuscript_and_verse_ids_at(verse):
            manuscript = Manuscript.objects.get(id=manuscript_id)

            verse = Verse.objects.get(id=verse_id)
            transcription = manuscript.transcription(verse)
            if transcription:
                transcriptions.append(transcription)
        return transcriptions
        
    def transcribed_manuscript_ids_at( self, verse, manuscript_ids=None ):
        if manuscript_ids is None:
            manuscript_ids = self.manuscript_ids_at(verse)
    
        transcriptions = self.transcriptions_at( verse, manuscript_ids=manuscript_ids )
        if not transcriptions:
            return set()
        return {transcription.manuscript.id for transcription in transcriptions}
    
    def untranscribed_manuscript_ids_at( self, verse ):
        manuscript_ids = self.manuscript_ids_at(verse)
        transcribed_manuscript_ids = self.transcribed_manuscript_ids_at( verse, manuscript_ids=manuscript_ids )

        return manuscript_ids - transcribed_manuscript_ids
        
    def untranscribed_manuscripts_at( self, verse ):
        return Manuscript.objects.filter(id__in=self.untranscribed_manuscript_ids_at(verse) )
    
    def add_manuscript_all(self, manuscript):
        """ Convenience function to add an AffiliationAll object to relate the group with the manuscript. """ 
        return self.add_manuscript_to_affiliation( AffiliationAll(), manuscript )

    def add_manuscript_at_verses( self, manuscript, verses ):
        """ Convenience function to add an AffiliationVerses object to relate the group with the manuscript. """     
        affiliation = self.add_manuscript_to_affiliation( AffiliationVerses(), manuscript )
        for verse in verses:
            if verse and isinstance( verse, Verse ):        
                affiliation.verses.add( verse )
        return affiliation
        
    def add_manuscript_range(self, manuscript, start_verse, end_verse):
        """ Convenience function to add an AffiliationRange object to relate the group with the manuscript. """     
        return self.add_manuscript_to_affiliation( AffiliationRange(start_verse=start_verse, end_verse=end_verse), manuscript )

    def add_affiliated_family_range( self, other_family, start_verse, end_verse ):
        """ Convenience function to add an AffiliationRange object to relate another family with this family. """     
        return self.add_family_to_affiliation( AffiliationRange(start_verse=start_verse, end_verse=end_verse), other_family )

    def affiliation_matrix(self, manuscripts, verses):
        """ 
        Returns an array of boolean values stating whether or not a manuscript is affliated with this family at any particular verse. 
        
        Returns a 2D numpy array of shape (len(manuscripts),len(verses)).
        """
        affiliation_matrix = np.zeros( (len(manuscripts),len(verses)), dtype=bool)
        
        for verse_index, verse in enumerate(verses):
            manuscript_ids = self.manuscript_ids_at(verse)
            for manuscript_index, manuscript in enumerate(manuscripts):
                affiliation_matrix[manuscript_index][verse_index] = (manuscript.id in manuscript_ids)
        return affiliation_matrix
       
    def get_verse_from_string(self, verse_string):
        """ Gets the Verse class from the manuscripts affliated with this manuscript and returns the verse with this ref. """
        classes_tried = set()
        for affiliation in self.affiliationbase_set.all():
            for manuscript in affiliation.manuscripts.all():
                verse_class = manuscript.verse_class()
                if verse_class in classes_tried:
                    continue

                verse = verse_class.get_from_string( verse_string )
                if verse:
                    return verse
                
                classes_tried.update( [verse_class] )
            
        return None


class Family(FamilyBase):
    class Meta:
        verbose_name_plural = 'Families'        
        

class AffiliationBase(PolymorphicModel):
    name = models.CharField(max_length=200, blank=True, help_text='A descriptive string for this affilitation.')
    families = models.ManyToManyField(FamilyBase, help_text="All the families that are affiliated through the relationship defined by this object.")
    manuscripts = models.ManyToManyField(Manuscript, blank=True, help_text="All the manuscripts that are affiliated to the families through the relationship defined by this object.")
    
    def __str__(self):
        if self.name:
            return self.name
            
        return "Affiliation %d" % self.id

    def is_active( self, verse ):
        """ Returns a boolean saying whether or not this affiliation is active for this verse. """        
        False
    
    def manuscript_ids( self ):
        """ Returns a set with the ids of all the manuscripts with this affiliation at any verse. """    
        return set( self.manuscripts.all().values_list('id', flat=True) )

    def family_ids( self ):
        """ Returns a set with the ids of all the families with this affiliation at any verse. """    
        return set( self.families.all().values_list('id', flat=True) )
        
    def manuscript_ids_at( self, verse ):
        """ Returns a set with the ids of all the manuscripts with this affiliation at a particular verse. """
        if self.is_active(verse):
            return self.manuscript_ids()
        return set()
        
    def manuscript_and_verse_ids_at( self, verse ):
        """ 
        Returns a set with the ids of all the manuscripts and the corresponding verses with this affiliation at a particular verse. 
        
        This is necessary if the affiliation uses indirect links to verses (like in lectionary verses in dcodex_lectionary)
        """
        if self.is_active(verse):
            return {(manuscript_id, verse.id) for manuscript_id in self.manuscript_ids()}
        return set()
        
    def manuscripts_at(self, verse):
        """ Returns a Django query set for all the manuscripts with this affiliation at a particular verse. """    
        return Manuscript.objects.filter( id__in=self.manuscript_ids_at(verse) )

    def family_ids_at( self, verse ):
        """ Returns a set with the ids of all the families with this affiliation at a particular verse. """    
        if self.is_active(verse):
            return self.family_ids()
        return set()
            
    def families_at( self, verse ):
        """ Returns a Django query set for all the families with this affiliation at a particular verse. """        
        return Family.objects.filter( id__in=self.family_ids_at(verse) )
    
    
    
class AffiliationAll(AffiliationBase):
    """ An Affiliation class which is active throughout every verse of the text except for verses in the 'exclude' field. """        
    exclude = models.ManyToManyField(Verse, blank=True, related_name='affiliation_exclude_verses', help_text="All the verses where this affiliation object is inactive.")

    def is_active( self, verse ):
        return not self.exclude.filter( id=verse.id ).exists()
        


class AffiliationVerses(AffiliationBase):
    """ An Affiliation class which is active within a list of verses. """        
    verses = models.ManyToManyField(Verse, related_name='affiliation_verses', help_text="All the verses where this affiliation object is active.")

    def __str__(self):
        parent_string = super().__str__()
        return  "%s at %s" % (parent_string, str(self.verses.all()) )

    def is_active( self, verse ):
        """ This affiliation is active at the verses associated in the 'verses' field of this class. """            
        return self.verses.filter( id=verse.id ).exists()
        
        
class AffiliationRange(AffiliationBase):
    """ An Affiliation class which is active within a range of verses in the manuscripts. """        
    start_verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='start_verse')
    end_verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='end_verse')
    exclude = models.ManyToManyField(Verse, related_name='affiliationrange_exclude_verses', blank=True, help_text="All the verses in this range where this affiliation object is actually inactive.")

    def __str__(self):
        parent_string = super().__str__()
        return  "%s from %s to %s" % (parent_string, self.start_verse.reference_abbreviation(), self.end_verse.reference_abbreviation())

    def is_active( self, verse ):
        """ The affiliation is active within the start and end verses (inclusive). """            
        return self.start_verse.rank <= verse.rank <= self.end_verse.rank and not self.exclude.filter( id=verse.id ).exists()
        
            
    
    
#https://simpleisbetterthancomplex.com/tutorial/2016/11/23/how-to-add-user-profile-to-django-admin.html
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reference_texts = models.ManyToManyField(Manuscript)
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

