
from django.urls import include, path
from .views import ResourceDetailView, getTagConcept, get_files, ExercisesList, overleaf_link, overleaf_link_series, \
    CartAPI, download_series
    #, ResourceList, ResourceListing, getAuthors, getLevel, getTagFamily, getCourse, getLanguage, getOntology

app_name = "document"

urlpatterns = [

    path('<slug:slug>', ResourceDetailView.as_view(), name='resource-detail'),
    path("ajax/tagconcept/", getTagConcept, name='autocomplete'),
    path("download/<int:obj_pk>", get_files, name='get_files'),
    path("overleaf/<slug:slug>", overleaf_link, name='overleaf_exercise'),
    path("overleaf_series/<str:id_list>", overleaf_link_series, name='overleaf_series'),
    path("download_series/<str:id_list>", download_series, name='download_series'),
    path('<str:ontologyRoot>/', ExercisesList.as_view(), name='exercises-list'),
    path('', ExercisesList.as_view(), name='exercises-list-no-filter'),
    path('<str:ontologyRoot>/<str:ontologyParent>/', ExercisesList.as_view(),
         name='exercises-list-parentOntology'),
    path('<str:ontologyRoot>/<str:ontologyParent>/<str:ontologyChild>', ExercisesList.as_view(),
         name='exercises-list-childOntology'),
    path("1/cart", CartAPI.as_view(), name='cart'),
    # Your stuff: custom urls includes go here
]
