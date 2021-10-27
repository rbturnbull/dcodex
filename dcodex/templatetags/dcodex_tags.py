from django import template
import logging

register = template.Library()


@register.filter
def manuscript_transcription(manuscript, verse):
    if not manuscript or not verse:
        return ""
    transcription = manuscript.transcription(verse)
    if not transcription:
        return ""
    return transcription.transcription


@register.filter
def blank_if_none(text):
    if text:
        return text
    return ""


@register.filter
def folio_name(manuscript, page_index):
    return manuscript.folio_name(page_index)


@register.filter
def folio_and_page(manuscript, page_index):
    folio_name = manuscript.folio_name(page_index)
    if folio_name:
        return f"{folio_name} – p. {page_index}"
    return f"Page {page_index}"


@register.simple_tag(takes_context=True)
def has_view_permission(context, manuscript):
    return manuscript.has_view_permission(context["user"])


@register.simple_tag(takes_context=True)
def has_change_permission(context, manuscript):
    return manuscript.has_change_permission(context["user"])
