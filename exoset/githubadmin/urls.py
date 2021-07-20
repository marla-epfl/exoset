from django.urls import include, path
from .views import list_pull_request, MetadataFormView, PullRequestDetail, merge_pull_request, \
    prerequisites_autocomplete, ResourceListAdmin
app_name = "githubadmin"

urlpatterns = [

    path("list_pull_request/", list_pull_request, name='pull_request_list'),
    path("metadata_creation/<id>/<str:folder_name>", MetadataFormView.as_view(), name='metadata_creation'),
    path("pull_request/<int:id>", PullRequestDetail.as_view(), name='pull_request_detail'),
    path("merge_pull/<int:pull_request_id>", merge_pull_request, name='pull_request_merge'),
    path("autocomplete_prerequisites", prerequisites_autocomplete, name='prerequisite_autocomplete'),
    path("list_resources_files", ResourceListAdmin.as_view(), name='list_resources_files')
    # Your stuff: custom urls includes go here
]
