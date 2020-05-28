from django.http import HttpResponse

from django.shortcuts import get_object_or_404, render
from django.template import loader

from dcodex.models import *
from dcodex.util import get_request_dict
from django.contrib.auth.decorators import login_required
import logging
import json
    
@login_required
def get_verse(request, manuscript):
    request_dict = get_request_dict(request)
    verse_id = request_dict.get('verse_id')
    return manuscript.verse_from_id( verse_id )

@login_required
def get_manuscript(request):
    request_dict = get_request_dict(request)
    return get_object_or_404(Manuscript, id=request_dict.get('manuscript_id'))   

@login_required
def get_pdf(request):
    request_dict = get_request_dict(request)
    return get_object_or_404(PDF, filename=request_dict.get('pdf_filename'))   

@login_required
def get_manuscript_and_verse(request):
    manuscript = get_manuscript(request)
    verse = get_verse(request, manuscript)
    return manuscript, verse

@login_required
def manuscript_verse_view(request, request_siglum, request_verse = None):
    logger = logging.getLogger(__name__)    

    if request_siglum.isdigit():
        manuscript = get_object_or_404(Manuscript, id=request_siglum)            
    else:
        manuscript = get_object_or_404(Manuscript, siglum=request_siglum)    
    logger.error(manuscript)
    logger.error(request_verse)

    if request_verse == None:
        verse = None
    elif request_verse.isdigit():
        verse = manuscript.verse_from_id( request_verse )        
    elif request_verse == 'empty':
        verse = manuscript.first_empty_verse()
    else:
        verse = manuscript.verse_from_string(request_verse)
        

    location = manuscript.location( verse )
    if verse is None:
        verse = location.verse
    transcription = manuscript.transcription( verse )
    
    context = {
        'manuscript': manuscript,
        'verse': verse,
        'transcription': transcription,
        'location': location,
    }
    return render(request, 'dcodex/manuscript.html', context)

@login_required
def thumbnails(request, pdf_filename):
    pdf    = get_object_or_404(PDF, filename=pdf_filename)   
    thumbnails = pdf.thumbnails( )
    
    return render(request, 'dcodex/thumbnails.html', {'thumbnails': thumbnails} )

@login_required
def pdf_images(request, pdf_filename):
    pdf    = get_object_or_404(PDF, filename=pdf_filename)   
    images = pdf.images( )
    
    return render(request, 'dcodex/pdf_images.html', {'images': images} )

@login_required
def page_locations_json(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    pdf        = get_pdf(request)
    page       = request_dict['page']
    
    locations = VerseLocation.objects.filter( manuscript=manuscript, pdf=pdf, page=page ).all()        
    
    list = [location.values_dict() for location in locations]
    return HttpResponse(json.dumps(list))
    
@login_required
def title_json(request):
    manuscript, verse = get_manuscript_and_verse(request)
    dict = manuscript.title_dict( verse )    
    return HttpResponse(json.dumps(dict))

@login_required
def verse_location_json(request):
    manuscript, verse = get_manuscript_and_verse(request)

    location = manuscript.location(verse)
    result = ""
    if location:
        result = json.dumps(location.values_dict())
    return HttpResponse(result)

@login_required
def verse_id(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    verse = manuscript.verse_from_dict(request_dict)
    if verse:
        return HttpResponse(verse.id)
    return HttpResponse("No verse found")

@login_required
def save_location(request):
    request_dict = get_request_dict(request)
    pdf = get_pdf(request)
    manuscript, verse = get_manuscript_and_verse(request)
    
    page = request_dict.get('page')
    x = request_dict.get('x')
    y = request_dict.get('y')

    location = manuscript.save_location( verse, pdf, page, x, y )
    
    return HttpResponse(json.dumps(location.values_dict()))

@login_required
def save_transcription(request):
    request_dict = get_request_dict(request)
    manuscript, verse = get_manuscript_and_verse(request)
    
    text = request_dict.get('transcription')
    transcription = manuscript.save_transcription( verse, text )
    next_verse = manuscript.next_verse( verse )
    next_verse_id_string = "%d" % (next_verse.id if next_verse else verse.id)
    
    
    return HttpResponse(next_verse_id_string)

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
def verse_ref_at_position(request):

    request_dict = get_request_dict(request)

    manuscript   = get_manuscript( request )
    
    pdf          = get_pdf(request)
    
    page         = int(request_dict.get('page'))
    x            = float(request_dict.get('x'))
    y            = float(request_dict.get('y'))
    
    verse = manuscript.approximate_verse_at_position( pdf, page, x, y )
    return render(request, 'dcodex/approx_verse.html', {'verse': verse} )

@login_required
def delete_location(request):
    manuscript, verse = get_manuscript_and_verse(request)
    
    location = manuscript.location( verse )
    location.delete()
    return HttpResponse('')

@login_required
def comparison(request):
    manuscript, verse = get_manuscript_and_verse(request)
    template = loader.get_template('dcodex/comparison.html')
#    $dcodex->comparisonTable("Reference", array($dcodex->getManuscript(18), $dcodex->getManuscript(16)), $verseID, $columns );
#    $dcodex->comparisonTableForGroups($manuscriptID, $verseID, $columns );
    
    reference_mss = request.user.profile.reference_texts.all()
    
    renders = []
    profile_reference = template.render({'heading': "Reference", 'comparison_texts': manuscript.comparison_texts( verse, reference_mss )}, request)
    renders.append( profile_reference )
    
    families = manuscript.families_at(verse)
    for family in families:
        renders.append( template.render({'heading': family.name, 'comparison_texts': family.transcriptions_at( verse )}, request) )
        
    all_mss = template.render({'heading': "All Transcribed", 'comparison_texts': manuscript.comparison_texts( verse )}, request)
    renders.append( all_mss )    
    return HttpResponse("".join(renders))

@login_required
def transcription_mini(request):
    manuscript, verse = get_manuscript_and_verse(request)    
    verse_transcription = manuscript.transcription( verse )
    location = manuscript.location( verse )
    
    return render(request, 'dcodex/transcription_mini.html', {'verse_transcription': verse_transcription, 'location': location} )
    
@login_required
def transcription_text(request):
    manuscript, verse = get_manuscript_and_verse(request)    
    verse_transcription = manuscript.transcription( verse )
    text = verse_transcription.transcription if verse_transcription else ""
    return HttpResponse(text)

@login_required
def page_number(request):
    request_dict = get_request_dict(request)
    pdf = get_pdf(request)
    folio_ref = request_dict['folio_ref']
    
    return HttpResponse(pdf.page_number(folio_ref) )

@login_required
def verse_search(request):
    manuscript, verse = get_manuscript_and_verse(request)
    return manuscript.render_verse_search( request, verse )

@login_required
def location_popup(request):
    manuscript, verse = get_manuscript_and_verse(request)

    return manuscript.render_location_popup( request, verse )    
    
@login_required
def select_manuscript(request):
    manuscripts = Manuscript.objects.all()
    return render(request, 'dcodex/select_manuscript.html', {'manuscripts': manuscripts} )

@login_required
def index(request):
    context = {'siglum': 1 + 3}
    return render(request, 'dcodex/index.html', context)
