
from django.urls import include, path
from .views import ResourceList, ResourceDetailView, gitHub_download, ResourceListing, getAuthors, getLevel, \
    getTagConcept, getTagFamily, getCourse, getLanguage, getOntology

app_name = "document"

urlpatterns = [

    path("", ResourceList),
    path('<slug:slug>', ResourceDetailView.as_view(), name='resource-detail'),
    path('success/', gitHub_download, name='github_download'),
    path("resources_listing/", ResourceListing.as_view(), name='listing'),
    path("ajax/author/", getAuthors, name='get_authors'),
    path("ajax/level/", getLevel, name='get_levels'),
    path("ajax/tagconcept/", getTagConcept, name='autocomplete'),
    path("ajax/tagproblemtype/", getTagFamily, name='get_tagfamily'),
    path("ajax/courses/", getCourse, name='get_course'),
    path("ajax/languages/", getLanguage, name='get_languages'),
    path("ajax/ontology/", getOntology, name='get_ontology'),
    # Your stuff: custom urls includes go here
]
