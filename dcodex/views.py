from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic import DetailView

from dcodex.models import *
from dcodex.util import get_request_dict


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

def get_deck_membership(request):
    request_dict = get_request_dict(request)
    deckmembershipid       = request_dict['deckmembershipid']
    return get_object_or_404( DeckMembership, id=deckmembershipid ) 

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
def thumbnails(request, request_siglum):
    lookup = dict(id=request_siglum) if request_siglum.isdigit() else dict(siglum=request_siglum)
    manuscript = get_object_or_404(Manuscript, **lookup)
    
    return render(request, 'dcodex/thumbnails.html', {'manuscript': manuscript} )


def ManuscriptDetailView(LoginRequiredMixin, DetailView):
    model = Manuscript
    slug_field = 'siglum'
    template_name = "manuscript_detail"


@login_required
def manuscript_tei_view(request, request_siglum ):
    lookup = dict(id=request_siglum) if request_siglum.isdigit() else dict(siglum=request_siglum)
    manuscript = get_object_or_404(Manuscript, **lookup)

    response = HttpResponse(manuscript.tei_string(), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{request_siglum}.xml"'
    return response


@login_required
def manuscript_latex_view(request, request_siglum ):
    lookup = dict(id=request_siglum) if request_siglum.isdigit() else dict(siglum=request_siglum)
    manuscript = get_object_or_404(Manuscript, **lookup)

    response = HttpResponse(manuscript.latex(), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{request_siglum}.tex"'
    return response


@login_required
def manuscript_accordance_view(request, request_siglum ):
    lookup = dict(id=request_siglum) if request_siglum.isdigit() else dict(siglum=request_siglum)
    manuscript = get_object_or_404(Manuscript, **lookup)

    response = HttpResponse(manuscript.accordance(), content_type='application/text charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{request_siglum}.txt"'
    return response


@login_required
def ms_images(request, request_siglum):
    lookup = dict(id=request_siglum) if request_siglum.isdigit() else dict(siglum=request_siglum)
    manuscript = get_object_or_404(Manuscript, **lookup)
    
    return render(request, 'dcodex/ms_images.html', {'manuscript': manuscript} )


@login_required
def page_locations_json(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    deck_membership = get_deck_membership(request)

    locations = VerseLocation.objects.filter( manuscript=manuscript, deck_membership=deck_membership ).all()        

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
    manuscript, verse = get_manuscript_and_verse(request)
    deck_membership = get_deck_membership(request)

    request_dict = get_request_dict(request)
    x = request_dict.get('x')
    y = request_dict.get('y')

    location = manuscript.save_location( verse, deck_membership, x, y )
    
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

    deck_membership = get_deck_membership(request)
    folio = request_dict.get('folio')
    side = request_dict.get('side')

    folio_ref, created = FolioRef.objects.update_or_create(
        deck_membership=deck_membership, 
        defaults={"folio": folio, "side": side}
    )
    return HttpResponse(created)


@login_required
def verse_ref_at_position(request):
    request_dict = get_request_dict(request)
    manuscript      = get_manuscript( request )
    deck_membership = get_deck_membership( request )    
    x               = float(request_dict.get('x'))
    y               = float(request_dict.get('y'))
    
    verse = manuscript.approximate_verse_at_position( deck_membership, x, y )
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
    ms_hover = loader.get_template('dcodex/ms_hover.html')
#    $dcodex->comparisonTable("Reference", array($dcodex->getManuscript(18), $dcodex->getManuscript(16)), $verseID, $columns );
#    $dcodex->comparisonTableForGroups($manuscriptID, $verseID, $columns );
    logger = logging.getLogger(__name__)    
    logger.error("in comparison")
    
    reference_mss = request.user.profile.reference_texts.all()
    
    renders = []
    profile_reference = template.render({'heading': "Reference", 'comparison_texts': manuscript.comparison_texts( verse, reference_mss )}, request)
    renders.append( profile_reference )
    
    families = manuscript.families_at(verse)
    for family in families:        
        renders.append( template.render({'heading': family.name, 'comparison_texts': family.transcriptions_at( verse )}, request) )
        untranscribed_manuscript_ids = family.untranscribed_manuscript_ids_at( verse ) - {manuscript.id}
        if len(untranscribed_manuscript_ids) > 0:
            untranscribed_manuscripts = Manuscript.objects.filter( id__in=untranscribed_manuscript_ids )
            renders.append( ms_hover.render( {'heading': 'Untranscribed', 'manuscripts': untranscribed_manuscripts, 'verse':verse}, request) )
        
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
    manuscript   = get_manuscript( request )
    folio_ref = request_dict['folio_ref']
    
    return HttpResponse(manuscript.page_number(folio_ref) )

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


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dcodex/home.html"
    extra_context = dict(
        manuscripts_with_decks=Manuscript.objects.exclude(imagedeck=None),
        manuscripts_without_decks=Manuscript.objects.filter(imagedeck=None),
    )
    