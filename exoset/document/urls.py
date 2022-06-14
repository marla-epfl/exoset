
from django.urls import include, path
from .views import ResourceList, ResourceDetailView, ResourceListing, getAuthors, getLevel, \
    getTagConcept, getTagFamily, getCourse, getLanguage, getOntology, get_files, ExercisesList

app_name = "document"

urlpatterns = [

    #path("", ResourceList, name='resource-list'),
    path('<slug:slug>', ResourceDetailView.as_view(), name='resource-detail'),
    #path("resources_listing/", ResourceListing.as_view(), name='listing'),
    #path("ajax/author/", getAuthors, name='get_authors'),
    #path("ajax/level/", getLevel, name='get_levels'),
    #path("ajax/tagconcept/", getTagConcept, name='autocomplete'),
    #path("ajax/tagproblemtype/", getTagFamily, name='get_tagfamily'),
    #path("ajax/courses/", getCourse, name='get_course'),
    #path("ajax/languages/", getLanguage, name='get_languages'),
    #path("ajax/ontology/", getOntology, name='get_ontology'),
    #path("download/<int:obj_pk>", get_files, name='get_files'),
    path('<str:ontologyRoot>/', ExercisesList.as_view(), name='exercises-list'),
    path('', ExercisesList.as_view(), name='exercises-list-no-filter'),
    path('<str:ontologyRoot>/<str:ontologyParent>/', ExercisesList.as_view(),
         name='exercises-list-parentOntology'),
    path('<str:ontologyRoot>/<str:ontologyParent>/<str:ontologyChild>', ExercisesList.as_view(),
         name='exercises-list-childOntology'),
    # Your stuff: custom urls includes go here
]
