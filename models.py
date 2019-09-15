from django.db import models
from django.conf import settings
from polymorphic.models import PolymorphicModel
from django.shortcuts import render
import re
from django.db.models import Max, Min
import os
import glob
import logging

def facsimile_dir():
    return settings.MEDIA_ROOT


# Create your models here.
class Manuscript(PolymorphicModel):
    manuscript_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    siglum = models.CharField(max_length=20, blank=True)
    def __str__(self):
        if self.name and self.siglum:
            if self.name == self.siglum:
                return self.siglum
            return "%s: %s" % (self.siglum, self.name)
        if self.name:
            return self.name
        if self.siglum:
            return self.siglum
        return str(self.manuscript_id)
    def short_name(self):
        if self.siglum:
            return self.siglum
        if self.name:
            return self.name
        return str(self.manuscript_id)
        
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
    def verse_from_dict(cls, dictionary):
        return cls.verse_class().get_from_dict( dictionary )

    def verse_search_template(self):
        raise NotImplementedError("Please implement this method")

    def render_verse_search( self, request, verse ):
        return render(request, self.verse_search_template(), {'verse': verse, 'manuscript': self} )
    
    def location_popup_template(self):
        raise NotImplementedError("Please implement this method")
    
    def render_location_popup( self, request, verse ):
        return render(request, self.location_popup_template(), {'verse': verse, 'manuscript': self} )
        
    def transcription( self, verse ):
        return self.transcription_class().objects.filter( manuscript=self, verse=verse ).first()
    
    def location_before_or_equal( self, verse ):
        return VerseLocation.objects.filter( manuscript=self, verse__id__lte=verse.id ).order_by('-verse__id').first()
        
    def location_after( self, verse ):
        return VerseLocation.objects.filter( manuscript=self, verse__id__gt=verse.id ).order_by('verse__id').first()
        
    def last_location( self, pdf ):
        return VerseLocation.objects.filter( manuscript=self, pdf=pdf ).order_by('-verse__id').first()
    def first_location( self, pdf ):
        return VerseLocation.objects.filter( manuscript=self, pdf=pdf ).order_by('verse__id').first()

    def location( self, verse ):
        location_A = self.location_before_or_equal( verse )
        
        # If this location is already saved then return it
        if location_A and verse.id == location_A.verse.id:
            return location_A

        # Find two locations to interpolate from
        if location_A is None:
            location_A = self.location_after( verse )
            if location_A is None: 
                return None

            location_B = self.last_location( pdf=location_A.pdf )
            if location_B is None or location_B.id == location_A.id:
                return location_A
        else:
            location_B = self.location_after( verse )
            if location_B is None:
                location_B = location_A;
                location_A = self.first_location( manuscript, map2.pdf )
                if location_A is None or location_A.id == location_B.id:
                    return location_B
    
        if location_A.pdf != location_B.pdf:
            return location_A
    
        textbox_top = VerseLocation.textbox_top(self)

        location_A_value = location_A.value( textbox_top ) 
        location_B_value = location_B.value( textbox_top ) 

        distance_verse_location_A = location_A.verse.distance_to(verse)
        distance_locations_B_location_A = location_A.verse.distance_to(location_B.verse)

        value_delta = (distance_verse_location_A)*(location_B_value - location_A_value)/(distance_locations_B_location_A)
    
        my_location_value = location_A_value + value_delta
        page = int(my_location_value)
        y = (my_location_value - page) * (1.0-2*textbox_top) + textbox_top
        
        return VerseLocation(manuscript=self, pdf=location_A.pdf, verse=verse, page=page, y=y, x=0.0)

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
        if not os.access(dir+src, os.R_OK):
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
    rank = models.IntegerField()
    def __str__(self):
        return self.reference()
    
    def reference(self, abbreviation = False, end_verse=None):
        if end_verse != None:
            return "%s–%s" % (self.reference( abbreviation=abbreviation ), end_verse.reference( abbreviation=abbreviation ) )
        return "%d" % (verse.pk)
    def reference_abbreviation(self):
        return self.reference(abbreviation = True)
    
    def next(self):
        return self.__class__.objects.filter( rank__gt=self.rank ).order_by('rank').first()

    def prev(self):
        return self.__class__.objects.filter( rank__lt=self.rank ).order_by('-rank').first()

    def cumulative_mass(self):
        return self.rank
        
    def distance_to(self, other_verse):
        return other_verse.cumulative_mass() - self.cumulative_mass()

    @classmethod
    def get_from_string( cls, verse_as_string ):
        return None

    @classmethod
    def get_from_dict( cls, dictionary ):
        return None
        
        
class Group(PolymorphicModel):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(Manuscript, through='Membership')
    def __str__(self):
        return self.name    

class Membership(models.Model):
    manuscript  = models.ForeignKey(Manuscript, on_delete=models.CASCADE)
    group       = models.ForeignKey(Group, on_delete=models.CASCADE)
    start_verse = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='start_verse', blank=True, null=True, default=None)
    end_verse   = models.ForeignKey(Verse, on_delete=models.CASCADE, related_name='end_verse', blank=True, null=True, default=None)
    def __str__(self):
        return "%s in %s (%s)" % (self.manuscript.short_name(), self.group.name, self.start_verse.reference(abbreviation=True, end_verse=self.end_verse) )
        
    
class VerseLocation(models.Model):
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE)
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    page = models.IntegerField()
    x = models.FloatField()
    y = models.FloatField()
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
        return {'manuscript_id': self.manuscript.manuscript_id, 'pdf_filename': self.pdf.filename, 'x':self.x, 'y':self.y, 'page':self.page, 'verse_id':self.verse.id, 'ref':self.verse.reference_abbreviation(), 'tooltip':'', 'exact': True if self.pk else False }
        

class VerseTranscriptionBase(PolymorphicModel):
    manuscript = models.ForeignKey(Manuscript, on_delete=models.CASCADE)
    verse = models.ForeignKey(Verse, on_delete=models.CASCADE)
    transcription = models.CharField(max_length=1024)
    def __str__(self):
        return "%s in %s: %s" % (self.verse.reference(abbreviation=True), self.manuscript.short_name(), self.transcription )

class VerseTranscription(VerseTranscriptionBase):
    def __str__(self):
        return super(VerseTranscription, self).__str__()
    