from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter

# Register your models here.
from .models import *

class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    raw_id_fields = ("start_verse","end_verse")
    
@admin.register(Group)    
class GroupAdmin(admin.ModelAdmin):
    inlines = [MembershipInline]
    
@admin.register(Membership)    
class MembershipAdmin(admin.ModelAdmin):
    autocomplete_fields = []
    raw_id_fields = ("start_verse","end_verse")
    
@admin.register(VerseTranscription)
class VerseTranscriptionChildAdmin(PolymorphicChildModelAdmin):
    base_model = VerseTranscription
    show_in_index = True  # makes child model admin visible in main admin site
    
    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.
    '''
    base_form = ...
    base_fieldsets = (
        ...
    )
    '''


#@admin.register(VerseTranscriptionBase)
class VerseTranscriptionBaseParentAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """
    base_model = VerseTranscriptionBase
    child_models = (VerseTranscription)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.


admin.site.register(PDF)
admin.site.register(VerseLocation)
admin.site.register(Page)


