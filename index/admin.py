from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from index.models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme")
    fields = ("user", "theme")
    list_filter = ("user",)
    model = Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ("username", "email", "is_staff", "get_theme", "date_joined", "last_login",)
    list_select_related = ("profile",)

    def get_theme(self, instance):
        return instance.profile.theme
    get_theme.short_description = "Theme"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
