from django.urls import include, path
from .views import list_pull_request, MetadataFormView, PullRequestDetail, merge_pull_request, \
    prerequisites_autocomplete, ResourceListAdmin, load_ontology_level1, publish_resource, concepts_autocomplete, \
    change_flag_option, AdminGithub
app_name = "githubadmin"

urlpatterns = [
    path('<str:github_repo>/', include([
        path("list_pull_request/", list_pull_request, name='pull_request_list'),
    #    path('task_list/<str:sort>/', ResourceListAdmin.as_view(), name='task_sort'),
        path("list_resources_files", ResourceListAdmin.as_view(), name='list_resources_files'),
        path("merge_pull/<int:pull_request_id>", merge_pull_request, name='pull_request_merge'),
        path("pull_request/<int:id>", PullRequestDetail.as_view(), name='pull_request_detail'),
        path("metadata_creation/<id>/<str:folder_name>", MetadataFormView.as_view(), name='metadata_creation'),
        path('ajax/resource_visible/', publish_resource, name="publish_resource"),
        path("change_flag", change_flag_option, name='change_flag_resource'),
    ])),
    path('list_repositories', AdminGithub.as_view(), name='list_repositories'),
    #path("list_pull_request/", list_pull_request, name='pull_request_list'),
    #path("metadata_creation/<id>/<str:folder_name>", MetadataFormView.as_view(), name='metadata_creation'),
    #path("pull_request/<int:id>", PullRequestDetail.as_view(), name='pull_request_detail'),
    #path("merge_pull/<int:pull_request_id>", merge_pull_request, name='pull_request_merge'),
    path("autocomplete_prerequisites", prerequisites_autocomplete, name='prerequisite_autocomplete'),
    path("autocomplete_concepts", concepts_autocomplete, name='concept_autocomplete'),
    #path("list_resources_files", ResourceListAdmin.as_view(), name='list_resources_files'),
    path('ajax/load-ontology_children/', load_ontology_level1, name='ajax_load_ontology'),
    #path('ajax/resource_visible/', publish_resource, name="publish_resource"),
    #path('task_list/<str:sort>/', ResourceListAdmin.as_view(), name='task_sort'),
    #path("change_flag", change_flag_option, name='change_flag_resource'),

    # Your stuff: custom urls includes go here
]
