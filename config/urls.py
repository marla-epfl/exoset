from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic.base import TemplateView, RedirectView
from django_tequila.urls import urlpatterns as django_tequila_urlpatterns
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from decorator_include import decorator_include
from exoset.ontology.models import Ontology


def only_user(group_name):
    def check(user):
        user_groups = user.groups.values_list('name', flat=True)
        if user.is_authenticated and group_name in user_groups:
            return True
        raise PermissionDenied
    return user_passes_test(check)


def root_ontology():
    return Ontology.get_root_nodes().values_list('name', flat=True)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n'), name='set_language'),
    path("", RedirectView.as_view(pattern_name='document:exercises-list-no-filter', permanent=False)),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html",
                                       extra_context=dict(list_parent_ontology=root_ontology())), name="about"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    #path("users/", include("exoset.users.urls", namespace="users")),
    #path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("resources/", include("exoset.document.urls", namespace="document")),
    path("admin_github/", decorator_include([login_required, only_user('github_user')],
         include("exoset.githubadmin.urls", namespace="githubadmin"))),
    path("graphapi/", include("exoset.graphapi.urls", namespace="graphapi")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += django_tequila_urlpatterns

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
