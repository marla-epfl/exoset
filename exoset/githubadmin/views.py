from django.shortcuts import render, get_object_or_404
from github import Github
from django.http import JsonResponse, HttpResponse
import json
import os
from .models import GitHubRepository
from django.core.exceptions import MultipleObjectsReturned
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import MetadataForm
from django.utils.translation import ugettext_lazy as _
from exoset.prerequisite.models import Prerequisite
from exoset.document.models import Resource, ResourceSourceFile
# Create your views here.


def new_exercises():
    """
    this function returns a list of exercises (folder) which are in the git repository but no Resource instance exists.
    """
    path_exercises = settings.MEDIA_ROOT + '/github/'

    existing_exercises = [x.source.split('/github/')[1] for x in ResourceSourceFile.objects.all()]
    exercises_from_github = [folder for folder in os.listdir(path_exercises) if os.path.isdir(path_exercises + folder)]
    x = set(existing_exercises)
    y = set(exercises_from_github)
    new_exercises_list = y.difference(x)
    if 'cartouche' in new_exercises_list:
        new_exercises_list.remove('cartouche')
    return new_exercises_list


def list_pull_request(request):
    data = {}
    try:
        github_repository = GitHubRepository.objects.get(official=True)
    except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
        return JsonResponse(data, status=200, safe=False)
    # g = Github("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")
    g = Github(github_repository.token)
    #open_pulls = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).get_pulls(state='open')
    #closed_pulls = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).get_pulls(state='closed')
    list_pulls = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).get_pulls(state='all')
    open_pulls = [x for x in list_pulls if x.state == 'open']
    #closed_pulls = [x for x in list_pulls if x.state == 'closed']
    list_open_pulls = {}
    list_closed_pulls = {}
    for open_pull in open_pulls:
        verified_pull = True
        metadata_file = True
        commit = list(open_pull.get_commits())[-1]
        for status in commit.get_check_runs():
            if status.name == 'build_latex' and status.conclusion == 'failure':
                verified_pull = False
                break
            elif status.name == 'check_file_metadata' and status.conclusion == 'failure':
                metadata_file = False
        if verified_pull:
            list_open_pulls[open_pull.number] = _("Pull request posted by {}  on {}. Contains all metadata: {}. "
                                                  ""
                                                  "Additional information: {} ; {}").format(open_pull.user.name,
                                                                                    open_pull.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                                                                                    str(metadata_file),
                                                                                    open_pull.title, open_pull.comments)
    #for closed_pull in closed_pulls:
    #    list_closed_pulls[closed_pull.number] = _("{}. Pull request posted by {} and merged on {}").format(
    #        closed_pull.title, closed_pull.user.name, closed_pull.merged_at
    #    )
    data['open'] = list_open_pulls
    #data['closed'] = list_closed_pulls
    return render(request, 'list_pull_request.html', {'data': data})


class MetadataFormView(FormView):
    template_name = 'metadata_form.html'
    form_class = MetadataForm
    success_url = '/thanks/'

    def get_form_kwargs(self, *args, **kwargs):
        """
        this function pass the client slug to form updating the kwargs['client']. This is needed to pass to the form
        the client (child) so initial value for accepted towns can be automatically checked. In form this information is
        retrieved to look for Client instance, checks the client's address and automatically check the option in the
        form based on the client's address town/department
        :param args:
        :param kwargs:
        :return:
        """
        kwargs = super(MetadataFormView, self).get_form_kwargs(*args, **kwargs)
        kwargs['id'] = self.kwargs['id']
        kwargs['exercise_folder_name'] = self.kwargs['folder_name']
        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        data = {}
        data['title'] = form.cleaned_data['title']
        data['language'] = form.cleaned_data['language']
        data['difficulty_level'] = form.cleaned_data['difficulty_level']
        data['question_type'] = form.cleaned_data['question_type']
        data['authors'] = form.cleaned_data['authors']
        data['family_problem'] = form.cleaned_data['family_problem']
        data['ontology0'] = form.cleaned_data['ontology0']
        data['ontology1'] = form.cleaned_data['ontology1']
        data['concept0'] = form.cleaned_data['concept0']
        data['concept1'] = form.cleaned_data['concept1']
        data['concept2'] = form.cleaned_data['concept2']
        data['concept3'] = form.cleaned_data['concept3']
        data['concept4'] = form.cleaned_data['concept4']
        data['prerequisite0'] = form.cleaned_data['prerequisite0']
        data['prerequisite1'] = form.cleaned_data['prerequisite1']
        data['prerequisite2'] = form.cleaned_data['prerequisite2']
        data['prerequisite3'] = form.cleaned_data['prerequisite3']
        data['prerequisite4'] = form.cleaned_data['prerequisite4']
        resource_id = self.kwargs['id']
        file_name = self.kwargs['folder_name'] + '_metadata.json'
        # PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge
        try:
            github_repository = GitHubRepository.objects.get(official=True)
        except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
            return JsonResponse(data, status=200, safe=False)
        # g = Github("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")
        path = settings.MEDIA_ROOT + '/github/'
        with open(path + file_name, 'w') as outfile:
            json.dump(data, outfile)
        g = Github(github_repository.token)
        administrator = g.get_user(github_repository.owner)
        repository = administrator.get_repo(github_repository.repository_name)
        # repository.get_pull(int(pull_request_id)).merge('changes approuved', 'exercice')
        # once created the metadata file a commit to the pull request is generated

        branch = repository.default_branch
        repository.create_git_commit("metadata file added")
        repository.create_pull("Metadata", "metadata")
        #test = repository.create_file(file_name, "automatic creation metadata", json.dumps(data, indent=4), branch=branch)
        #repository.update_file('data4.txt', "automatic creation metadata file 5", 'metadatafile 5', branch=pull_request_branch)


        return super().form_valid(form)


class PullRequestDetail(TemplateView):
    template_name = 'pullrequest_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PullRequestDetail, self).get_context_data(*args, **kwargs)
        data = {}
        try:
            github_repository = GitHubRepository.objects.get(official=True)
        except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
            return JsonResponse(data, status=200, safe=False)
        g = Github(github_repository.token)
        pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).get_pull(self.kwargs['id'])
        context['pull_request'] = pull_request
        return context


def merge_pull_request(request, pull_request_id):
    github_repository = GitHubRepository.objects.get(official=True)
    g = Github(github_repository.token)
    pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).\
        get_pull(pull_request_id)
    #merge = pull_request.merge()
    merge = False
    if merge:
        return HttpResponseRedirect(reverse('githubadmin:pull_request_list'))
    else:
        return render(request, 'error_merge.html')


def prerequisites_autocomplete(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        search_qs = list(Prerequisite.objects.filter(label__icontains=q).values('label').distinct())
        concepts_list = [i for i in search_qs]
        data = {
            'tagsconcepts': concepts_list,
        }
        return JsonResponse(data, status=200, safe=False)


def save_metadata(request, pk):
    resource_instance = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = MetadataForm(request.POST)
        if form.is_valid():
            # create objects
            return HttpResponseRedirect(reverse('githubadmin:pull_request_list'))


class ResourceListAdmin(ListView):
    model = ResourceSourceFile
    template_name = 'list_resources_files.html'

    def get_context_data(self, **kwargs):
        context = super(ResourceListAdmin, self).get_context_data(**kwargs)
        context['new_exercises'] = new_exercises
        return context
