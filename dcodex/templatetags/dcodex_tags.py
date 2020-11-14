from django import template
import logging

register = template.Library()

@register.filter
def manuscript_transcription(manuscript, verse):
    if not manuscript or not verse:
        return ""
    transcription = manuscript.transcription( verse )
    if not transcription:
        return ""
    return transcription.transcription

@register.filter
def blank_if_none(text):
    if text:
        return text
    return ""