from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic import DetailView, FormView
from django.core.exceptions import PermissionDenied
from dcodex.models import *
from dcodex.util import get_request_dict
from django.http import Http404

from .forms import PlotRollingAverageForm

import logging
import json


def get_verse(request, manuscript):
    request_dict = get_request_dict(request)
    verse_id = request_dict.get("verse_id")
    logging.error(f"in get_verse. {verse_id =}")
    return manuscript.verse_from_id(verse_id)


def get_deck_membership(request):
    request_dict = get_request_dict(request)
    deckmembershipid = request_dict["deckmembershipid"]
    return get_object_or_404(DeckMembership, id=deckmembershipid)


def get_manuscript_and_verse(request, change=False):
    manuscript = get_manuscript(request, change=change)
    verse = get_verse(request, manuscript)
    return manuscript, verse


def get_manuscript(request, request_siglum=None, change=False):
    """
    Returns a manuscript sought after.

    If the 'change' flag is True, then it checks if the permissions allow for changing the manuscript.
    """
    if request_siglum:
        lookup = (
            dict(id=request_siglum)
            if request_siglum.isdigit()
            else dict(siglum=request_siglum)
        )
    else:
        request_dict = get_request_dict(request)
        lookup = dict(id=request_dict.get("manuscript_id"))

    manuscript = get_object_or_404(Manuscript, **lookup)

    if not manuscript.has_view_permission(request.user):
        raise PermissionDenied()

    if change and not manuscript.has_change_permission(request.user):
        raise PermissionDenied()

    return manuscript


def manuscript_verse_view(request, request_siglum, request_verse=None):
    manuscript = get_manuscript(request, request_siglum)

    if request_verse == None:
        verse = None
    elif request_verse.isdigit():
        verse = manuscript.verse_from_id(request_verse)
    elif request_verse == "empty":
        verse = manuscript.first_empty_verse()
    else:
        verse = manuscript.verse_from_string(request_verse)

    location = manuscript.location(verse)
    if verse is None and location:
        verse = location.verse

    if verse:
        transcription = manuscript.transcription(verse)
    else:
        transcription = manuscript.first_transcription()
        if transcription:
            verse = transcription.verse

    # If no verse has been selected, then just find the first verse in the class of verses for this manuscript
    if not verse:
        verse = manuscript.verse_class().objects.first()
        if not verse:
            raise Http404(f"Verse ({request_verse}) does not exist.")

    if not verse:
        raise Http404(f"Verse ({request_verse}) does not exist.")

    context = {
        "manuscript": manuscript,
        "verse": verse,
        "transcription": transcription,
        "location": location,
    }
    return render(request, "dcodex/manuscript.html", context)


def thumbnails(request, request_siglum):
    lookup = (
        dict(id=request_siglum)
        if request_siglum.isdigit()
        else dict(siglum=request_siglum)
    )
    manuscript = get_manuscript(request, request_siglum)

    return render(request, "dcodex/thumbnails.html", {"manuscript": manuscript})


# def ManuscriptDetailView(LoginRequiredMixin, DetailView):
#     model = Manuscript
#     slug_field = 'siglum'
#     template_name = "manuscript_detail"


def manuscript_tei_view(request, request_siglum):
    lookup = (
        dict(id=request_siglum)
        if request_siglum.isdigit()
        else dict(siglum=request_siglum)
    )
    manuscript = get_manuscript(request, request_siglum)

    response = HttpResponse(
        manuscript.tei_string(), content_type="application/text charset=utf-8"
    )
    response["Content-Disposition"] = f'attachment; filename="{request_siglum}.xml"'
    return response


def manuscript_latex_view(request, request_siglum):
    lookup = (
        dict(id=request_siglum)
        if request_siglum.isdigit()
        else dict(siglum=request_siglum)
    )
    manuscript = get_manuscript(request, request_siglum)

    response = HttpResponse(
        manuscript.latex(), content_type="application/text charset=utf-8"
    )
    response["Content-Disposition"] = f'attachment; filename="{request_siglum}.tex"'
    return response


def manuscript_accordance_view(request, request_siglum):
    manuscript = get_manuscript(request, request_siglum)

    response = HttpResponse(
        manuscript.accordance(), content_type="application/text charset=utf-8"
    )
    response["Content-Disposition"] = f'attachment; filename="{request_siglum}.txt"'
    return response


def ms_images(request, request_siglum):
    manuscript = get_manuscript(request, request_siglum)
    return render(request, "dcodex/ms_images.html", {"manuscript": manuscript})


def page_locations_json(request):
    manuscript = get_manuscript(request)
    deck_membership = get_deck_membership(request)

    locations = VerseLocation.objects.filter(
        manuscript=manuscript, deck_membership=deck_membership
    ).all()

    list = [location.values_dict() for location in locations]
    return HttpResponse(json.dumps(list))


def title_json(request):
    manuscript, verse = get_manuscript_and_verse(request)
    dict = manuscript.title_dict(verse)
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
    if verse:
        return HttpResponse(verse.id)
    return HttpResponse("No verse found")


def save_location(request):
    manuscript, verse = get_manuscript_and_verse(request, change=True)
    deck_membership = get_deck_membership(request)

    request_dict = get_request_dict(request)
    x = request_dict.get("x")
    y = request_dict.get("y")

    location = manuscript.save_location(verse, deck_membership, x, y)

    return HttpResponse(json.dumps(location.values_dict()))


def save_transcription(request):
    request_dict = get_request_dict(request)
    manuscript, verse = get_manuscript_and_verse(request, change=True)

    text = request_dict.get("transcription")
    transcription = manuscript.save_transcription(verse, text)
    next_verse = manuscript.next_verse(verse)
    next_verse_id_string = "%d" % (next_verse.id if next_verse else verse.id)

    return HttpResponse(next_verse_id_string)


@login_required
def save_folio_ref(request):
    request_dict = get_request_dict(request)

    deck_membership = get_deck_membership(request)

    # Check permissions
    has_change_permission = False
    for manuscript in deck_membership.deck.manuscript_set.all():
        if manuscript.has_change_permission(request.user):
            has_change_permission = True
    if not has_change_permission:
        raise PermissionDenied()

    folio = request_dict.get("folio")
    side = request_dict.get("side")

    folio_ref, created = FolioRef.objects.update_or_create(
        deck_membership=deck_membership, defaults={"folio": folio, "side": side}
    )
    return HttpResponse(created)


def verse_ref_at_position(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    deck_membership = get_deck_membership(request)
    x = float(request_dict.get("x"))
    y = float(request_dict.get("y"))

    verse = manuscript.approximate_verse_at_position(deck_membership, x, y)
    return render(request, "dcodex/approx_verse.html", {"verse": verse})


def delete_location(request):
    manuscript, verse = get_manuscript_and_verse(request, change=True)

    location = manuscript.location(verse)
    location.delete()
    return HttpResponse("")


def filter_transcriptions_viewable(transcriptions, user):
    return [
        transcription
        for transcription in transcriptions
        if transcription.manuscript.has_view_permission(user)
    ]


def filter_manuscripts_viewable(manuscripts, user):
    manuscripts = [
        manuscript for manuscript in manuscripts if manuscript.has_view_permission(user)
    ]
    logging.error(manuscripts)
    return manuscripts


def comparison(request):
    manuscript, verse = get_manuscript_and_verse(request)
    template = loader.get_template("dcodex/comparison.html")
    ms_hover = loader.get_template("dcodex/ms_hover.html")
    #    $dcodex->comparisonTable("Reference", array($dcodex->getManuscript(18), $dcodex->getManuscript(16)), $verseID, $columns );
    #    $dcodex->comparisonTableForGroups($manuscriptID, $verseID, $columns );

    reference_mss = (
        request.user.profile.reference_texts.all()
        if hasattr(request.user, "profile")
        else ""
    )

    renders = []
    reference_comparison_texts = filter_transcriptions_viewable(
        manuscript.comparison_texts(verse, reference_mss), request.user
    )
    profile_reference = template.render(
        {"heading": "Reference", "comparison_texts": reference_comparison_texts},
        request,
    )
    renders.append(profile_reference)

    families = manuscript.families_at(verse)
    for family in families:
        family_transcriptions = filter_transcriptions_viewable(
            family.transcriptions_at(verse), request.user
        )
        renders.append(
            template.render(
                {"heading": family.name, "comparison_texts": family_transcriptions},
                request,
            )
        )
        untranscribed_manuscript_ids = family.untranscribed_manuscript_ids_at(verse) - {
            manuscript.id
        }
        if len(untranscribed_manuscript_ids) > 0:
            untranscribed_manuscripts = Manuscript.objects.filter(
                id__in=untranscribed_manuscript_ids
            )
            untranscribed_manuscripts = [
                manuscript
                for manuscript in untranscribed_manuscripts
                if manuscript.has_view_permission(request.user)
            ]
            renders.append(
                ms_hover.render(
                    {
                        "heading": "Untranscribed",
                        "manuscripts": untranscribed_manuscripts,
                        "verse": verse,
                    },
                    request,
                )
            )

    all_transcriptions = filter_transcriptions_viewable(
        manuscript.comparison_texts(verse), request.user
    )
    all_mss = template.render(
        {"heading": "All Transcribed", "comparison_texts": all_transcriptions}, request
    )
    renders.append(all_mss)
    return HttpResponse("".join(renders))


def transcription_mini(request):
    manuscript, verse = get_manuscript_and_verse(request)
    verse_transcription = manuscript.transcription(verse)
    location = manuscript.location(verse)

    return render(
        request,
        "dcodex/transcription_mini.html",
        {"verse_transcription": verse_transcription, "location": location},
    )


def transcription_text(request):
    manuscript, verse = get_manuscript_and_verse(request)
    verse_transcription = manuscript.transcription(verse)
    text = verse_transcription.transcription if verse_transcription else ""
    return HttpResponse(text)


def page_number(request):
    request_dict = get_request_dict(request)
    manuscript = get_manuscript(request)
    folio_ref = request_dict["folio_ref"]

    return HttpResponse(manuscript.page_number(folio_ref))


def verse_search(request):
    manuscript, verse = get_manuscript_and_verse(request)
    return manuscript.render_verse_search(request, verse)


def location_popup(request):
    manuscript, verse = get_manuscript_and_verse(request)

    return manuscript.render_location_popup(request, verse)


@login_required
def select_manuscript(request):
    manuscripts = Manuscript.objects.all()
    return render(
        request, "dcodex/select_manuscript.html", {"manuscripts": manuscripts}
    )


class HomeView(TemplateView):
    template_name = "dcodex/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manuscripts_with_decks"] = filter_manuscripts_viewable(
            Manuscript.objects.exclude(imagedeck=None), self.request.user
        )
        context["manuscripts_without_decks"] = filter_manuscripts_viewable(
            Manuscript.objects.filter(imagedeck=None), self.request.user
        )
        return context


class PlotRollingSimilarity(FormView):
    template_name = "dcodex/form.html"
    form_class = PlotRollingAverageForm

    def form_valid(self, form):
        svg_data = form.get_svg_data()
        return HttpResponse(svg_data, content_type="image/svg+xml")
