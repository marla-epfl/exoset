
from django.urls import include, path
from .views import NotebookList, NotebookDetailView, FileExplorerTemplateView
app_name = "notebook"

urlpatterns = [
    path("", NotebookList.as_view(), name='notebook_list'),
    path("<slug:slug>", NotebookDetailView.as_view(), name='notebook_detail'),

    # Your stuff: custom urls includes go here
]
