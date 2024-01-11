from django.urls import include, path
from .views import ListExercises
app_name = "graphapi"

urlpatterns = [
    path('', ListExercises.as_view(), name='graph_api'),
    ]
