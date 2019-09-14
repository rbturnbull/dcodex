from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render

from dcodex.models import *
from django.contrib.auth.decorators import login_required

from project_dcodex.settings import STATIC_ROOT
import logging
import json

def get_request_dict(request):
    return request.POST if request.method == "POST" else request.GET
    
def get_verse(request, manuscript):
    request_dict = get_request_dict(request)
    return get_object_or_404(manuscript.verse_class(), id=request_dict.get('verse_id'))

def get_manuscript(request):
    request_dict = get_request_dict(request)
    return get_object_or_404(Manuscript, manuscript_id=request_dict.get('manuscript_id'))   

def get_pdf(request):
    request_dict = get_request_dict(request)
    return get_object_or_404(PDF, filename=request_dict.get('pdf_filename'))   

def get_manuscript_and_verse(request):
    manuscript = get_manuscript(request)
    verse = get_verse(request, manuscript)
    return manuscript, verse

def manuscript_verse_view(request, request_siglum, request_verse = None):
    logger = logging.getLogger(__name__)    

    if request_siglum.isdigit():
        manuscript = get_object_or_404(Manuscript, manuscript_id=request_siglum)            
    else:
        manuscript = get_object_or_404(Manuscript, siglum=request_siglum)    
    logger.error(manuscript)
    logger.error(request_verse)

    if request_verse and request_verse.isdigit():
        verse = manuscript.verse_class().objects.get(id=request_verse)
    else:
        verse = manuscript.verse_from_string(request_verse)
        
    transcription = manuscript.transcription( verse )
    location = manuscript.location( verse )

    context = {
        'manuscript': manuscript,
        'verse': verse,
        'transcription': transcription,
        'location': location,
    }
    return render(request, 'dcodex/manuscript.html', context)

static_dir = "/Users/rob/Ridley/ArabicManuscripts/DCodex/project_dcodex/dcodex/static/" # BIG HACK

def thumbnails(request, pdf_filename):
    pdf    = get_object_or_404(PDF, filename=pdf_filename)   
    thumbnails = pdf.thumbnails( static_dir )
    
    return render(request, 'dcodex/thumbnails.html', {'thumbnails': thumbnails} )

def pdf_images(request, pdf_filename):
    pdf    = get_object_or_404(PDF, filename=pdf_filename)   
    images = pdf.images( static_dir )
    
    return render(request, 'dcodex/pdf_images.html', {'images': images} )

def page_locations_json(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    pdf        = get_pdf(request)
    page       = request_dict['page']
    
    locations = VerseLocation.objects.filter( manuscript=manuscript, pdf=pdf, page=page ).all()        
    
    list = [location.values_dict() for location in locations]
    return HttpResponse(json.dumps(list))
def title_json(request):
    manuscript, verse = get_manuscript_and_verse(request)
    
    ref = verse.reference_abbreviation()
    
    dict = { 
        'title': "%s – %s" % (manuscript.siglum, ref), 
        'url': "/dcodex/ms/%s/%s/" % ( manuscript.siglum, ref.replace(" ", "") ) 
    }
    
    return HttpResponse(json.dumps(dict))
    
def verse_location_json(request):
    manuscript, verse = get_manuscript_and_verse(request)

    location = manuscript.location(verse)
    result = ""
    if location:
        result = json.dumps(location.values_dict())
    return HttpResponse(result)

def verse_id(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    verse = manuscript.verse_from_dict(request_dict)
    return HttpResponse(verse.id)

@login_required
def save_location(request):
    pdf = get_pdf(request)
    manuscript, verse = get_manuscript_and_verse(request)
    
    page = request_dict.get('page')
    x = request_dict.get('x')
    y = request_dict.get('y')

    location, created = VerseLocation.objects.update_or_create(
        manuscript=manuscript, 
        verse=verse, 
        defaults={"pdf": pdf, "page": page, 'x':x, 'y':y}
    )
    return HttpResponse(json.dumps(location.values_dict()))

@login_required
def save_transcription(request):
    manuscript, verse = get_manuscript_and_verse(request)
    
    transcription = request_dict.get('transcription')

    transcription, created = manuscript.transcription_class().objects.update_or_create(
        manuscript=manuscript, 
        verse=verse, 
        defaults={"transcription": transcription}
    )
    return HttpResponse('')

@login_required
def save_folio_ref(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    pdf = get_pdf(request)
    
    page = request_dict.get('page')
    folio = request_dict.get('folio')
    side = request_dict.get('side')

    page, created = Page.objects.update_or_create(
        manuscript=manuscript, 
        pdf=pdf, 
        page=page, 
        defaults={"folio": folio, "side": side}
    )
    return HttpResponse(created)

@login_required
def delete_location(request):
    manuscript, verse = get_manuscript_and_verse(request)
    
    location = manuscript.location( verse )
    location.delete()
    return HttpResponse('')

def comparison(request):
    manuscript, verse = get_manuscript_and_verse(request)
    
#    $dcodex->comparisonTable("Reference", array($dcodex->getManuscript(18), $dcodex->getManuscript(16)), $verseID, $columns );
#    $dcodex->comparisonTableForGroups($manuscriptID, $verseID, $columns );
    
    comparison_texts = manuscript.transcription_class().objects.filter( verse=verse ).all()        
    
    
    logger = logging.getLogger(__name__)    
    logger.error(manuscript)
    
    return render(request, 'dcodex/comparison.html', {'heading': "All Transcribed", 'comparison_texts': comparison_texts} )

def transcription_mini(request):
    manuscript, verse = get_manuscript_and_verse(request)    
    verse_transcription = manuscript.transcription_class().objects.filter( manuscript=manuscript, verse=verse ).first()
    location = manuscript.location( verse )
    
    return render(request, 'dcodex/transcription_mini.html', {'verse_transcription': verse_transcription, 'location': location} )
def transcription_text(request):
    manuscript, verse = get_manuscript_and_verse(request)    
    verse_transcription = manuscript.transcription_class().objects.filter( manuscript=manuscript, verse=verse ).first()
    text = verse_transcription.transcription if verse_transcription else ""
    return HttpResponse(text)

def page_number(request):
    request_dict = get_request_dict(request)
    pdf = get_pdf(request)
    folio_ref = request_dict['folio_ref']
    
    return HttpResponse(pdf.page_number(folio_ref) )

def verse_search(request):
    manuscript, verse = get_manuscript_and_verse(request)
    return manuscript.render_verse_search( request, verse )

def location_popup(request):
    manuscript, verse = get_manuscript_and_verse(request)
    return manuscript.render_location_popup( request, verse )    
    
def select_manuscript(request):
    manuscripts = Manuscript.objects.all()
    return render(request, 'dcodex/select_manuscript.html', {'manuscripts': manuscripts} )
    
def index(request):
    context = {'siglum': 1 + 3}
    return render(request, 'dcodex/index.html', context)