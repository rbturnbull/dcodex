from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from guardian.admin import GuardedModelAdminMixin, GuardedModelAdmin


from .models import *

# class MembershipInline(admin.TabularInline):
#    model = Membership
#    extra = 0
#    raw_id_fields = ("start_verse","end_verse")

# class ManuscriptChildAdmin(GuardedModelAdminMixin, PolymorphicChildModelAdmin):
#     """ Base admin class for all child models of Manuscript """
#     base_model = Manuscript


class ManuscriptChildAdmin(GuardedModelAdmin):
    base_model = Manuscript
    search_fields = ["siglum", "name"]


# @admin.register(Manuscript)
# class ManuscriptParentAdmin(PolymorphicParentModelAdmin):
#     """ The parent model admin """
#     base_model = Manuscript  # Optional, explicitly set here.
#     child_models = ()
#     list_filter = (PolymorphicChildModelFilter,)  # This is optional.


class AffiliationChildAdmin(PolymorphicChildModelAdmin):
    base_model = AffiliationBase  # Optional, explicitly set here.

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.


#    base_form =
#    base_fieldsets = (
#    )


@admin.register(AffiliationAll)
class AffiliationAllAdmin(AffiliationChildAdmin):
    base_model = AffiliationAll
    show_in_index = True  # makes child model admin visible in main admin site


@admin.register(AffiliationVerses)
class AffiliationVersesAdmin(AffiliationChildAdmin):
    base_model = AffiliationVerses
    show_in_index = True  # makes child model admin visible in main admin site


@admin.register(AffiliationRange)
class AffiliationRangeAdmin(AffiliationChildAdmin):
    base_model = AffiliationRange
    raw_id_fields = (
        "start_verse",
        "end_verse",
    )

    show_in_index = True  # makes child model admin visible in main admin site


@admin.register(AffiliationBase)
class AffiliationBaseAdmin(PolymorphicParentModelAdmin):
    base_model = AffiliationBase
    child_models = (AffiliationAll,)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    show_in_index = False


class FamilyChildAdmin(PolymorphicChildModelAdmin):
    base_model = FamilyBase  # Optional, explicitly set here.

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.


#    base_form =
#    base_fieldsets = (
#    )


@admin.register(FamilyBase)
class FamilyBaseAdmin(PolymorphicParentModelAdmin):
    base_model = FamilyBase
    child_models = (Family,)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.
    show_in_index = False


@admin.register(Family)
class FamilyAdmin(FamilyChildAdmin):
    base_model = Family
    show_in_index = True  # makes child model admin visible in main admin site


# @admin.register(Membership)
# class MembershipAdmin(admin.ModelAdmin):
#    autocomplete_fields = []
#    raw_id_fields = ("start_verse","end_verse")


@admin.register(VerseTranscription)
class VerseTranscriptionChildAdmin(PolymorphicChildModelAdmin):
    base_model = VerseTranscription
    show_in_index = True  # makes child model admin visible in main admin site
    search_fields = ("manuscript__siglum", "transcription")

    # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
    # the additional fields of the child models are automatically added to the admin form.
    """
    base_form = ...
    base_fieldsets = (
        ...
    )
    """


# @admin.register(VerseTranscriptionBase)
class VerseTranscriptionBaseParentAdmin(PolymorphicParentModelAdmin):
    """The parent model admin"""

    base_model = VerseTranscriptionBase
    child_models = VerseTranscription
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.


admin.site.register(StandardMarkup)
admin.site.register(MinimalMarkup)
admin.site.register(SimpleArabicMarkup)

admin.site.register(PDF)
admin.site.register(VerseLocation)
admin.site.register(Page)
admin.site.register(FolioRef)


# https://simpleisbetterthancomplex.com/tutorial/2016/11/23/how-to-add-user-profile-to-django-admin.html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()
# UserAdmin = admin.site._registry[User]


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
