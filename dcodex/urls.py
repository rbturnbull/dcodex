from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path(
        "ms/<str:request_siglum>/",
        views.manuscript_verse_view,
        name="dcodex-manuscript",
    ),
    path(
        "ms/<str:request_siglum>/thumbnails/",
        views.thumbnails,
        name="dcodex-thumbnails",
    ),
    path(
        "ms/<str:request_siglum>/<str:request_verse>/",
        views.manuscript_verse_view,
        name="dcodex-manuscript-verse",
    ),
    path(
        "ms/tei/<str:request_siglum>/",
        views.manuscript_tei_view,
        name="dcodex-manuscript-tei",
    ),
    path(
        "ms/accordance/<str:request_siglum>/",
        views.manuscript_accordance_view,
        name="dcodex-manuscript-accordance",
    ),
    path(
        "ms/latex/<str:request_siglum>/",
        views.manuscript_latex_view,
        name="dcodex-manuscript-latex",
    ),
    path(
        "ajax/ms-images/<str:request_siglum>/", views.ms_images, name="dcodex-ms-images"
    ),
    path(
        "ajax/page-locations-json/",
        views.page_locations_json,
        name="dcodex-page-locations-json",
    ),
    path(
        "ajax/verse-location-json/",
        views.verse_location_json,
        name="dcodex-verse-location-json",
    ),
    path("ajax/verse-id/", views.verse_id, name="dcodex-verse-id"),
    path("ajax/comparison/", views.comparison, name="dcodex-comparison"),
    path(
        "ajax/transcription-mini/",
        views.transcription_mini,
        name="dcodex-transcription-mini",
    ),
    path("ajax/verse-search/", views.verse_search, name="dcodex-verse-search"),
    path("ajax/location-popup/", views.location_popup, name="dcodex-location-popup"),
    path(
        "ajax/select-manuscript/",
        views.select_manuscript,
        name="dcodex-select-manuscript",
    ),
    path(
        "ajax/transcription-text/",
        views.transcription_text,
        name="dcodex-transcription-text",
    ),
    path("ajax/page-number/", views.page_number, name="dcodex-page-number"),
    path("ajax/save-folio-ref/", views.save_folio_ref, name="dcodex-save-folio-ref"),
    path("ajax/save-location/", views.save_location, name="dcodex-save-location"),
    path(
        "ajax/save-transcription/",
        views.save_transcription,
        name="dcodex-save-transcription",
    ),
    path("ajax/delete-location/", views.delete_location, name="dcodex-delete-location"),
    path("ajax/title-json/", views.title_json, name="dcodex-title-json"),
    path(
        "ajax/verse_ref_at_position/",
        views.verse_ref_at_position,
        name="dcodex-verse_ref_at_position",
    ),
    path(
        "plot-rolling-similarity",
        views.PlotRollingSimilarity.as_view(),
        name="plot-rolling-similarity",
    ),
]
