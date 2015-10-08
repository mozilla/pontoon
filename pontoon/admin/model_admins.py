from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin, UserAdmin as AuthUserAdmin
from django.contrib.auth.models import Group, User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from pontoon.admin.site import admin_site
from pontoon.base.models import (
    UserProfile,
    Locale,
    Project,
    Subpage,
    Repository,
    Resource,
    Entity,
    Translation,
    Stats,
)


class SubpageInline(admin.TabularInline):
    model = Subpage
    extra = 0
    fields = ('project', 'name', 'url', 'resources')
    raw_id_fields = ('resources',)


class RepositoryInline(admin.TabularInline):
    model = Repository
    extra = 0
    fields = ('type', 'url', 'source_repo')


@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'latest_activity')
    search_fields = ('name',)
    filter_horizontal = ('locales',)

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'info_brief', 'locales'),
        }),
        ('Website', {
            'fields': ('url', 'width', 'links'),
        }),
    )

    inlines = (RepositoryInline, SubpageInline)

    def latest_activity(self, project):
        """Generate latest activity display string."""
        activity = project.latest_activity()
        if activity is None or not activity['date']:
            return u'No activity yet'
        else:
            display_string = naturaltime(activity['date'])

            user = activity['user']
            if user is not None:
                display_string += format_html(
                    u'&bull; <a href="{url}">{username}</a>',
                    url=reverse('admin:auth_user_change', args=(user.pk,)),
                    username=user.display_name,
                )

            return display_string
    latest_activity.allow_tags = True


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    max_num = 1
    can_delete = False
    fields = ('quality_checks',)


@admin.register(User, site=admin_site)
class UserAdmin(AuthUserAdmin):
    """Configuration for the user admin pages."""
    inlines = (UserProfileInline,)


# Default ModelAdmins
admin_site.register(Locale)
admin_site.register(Resource)
admin_site.register(Entity)
admin_site.register(Translation)
admin_site.register(Stats)
admin_site.register(Group, GroupAdmin)
