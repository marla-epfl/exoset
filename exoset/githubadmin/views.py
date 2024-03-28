from django.shortcuts import render, get_object_or_404
from github import Github
from django.http import JsonResponse, HttpResponse
from datetime import datetime
import git
import os
import requests
from .models import GitHubRepository
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import File
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from .forms import MetadataForm, ResourceForm, FlagForm
from django.utils.translation import gettext_lazy as _
from exoset.prerequisite.models import Prerequisite
from exoset.document.models import Resource, ResourceSourceFile, Document, update_filename
from exoset.ontology.models import Ontology, DocumentCategory
from exoset.tag.models import TagLevelResource, TagProblemTypeResource, TagProblemType, QuestionTypeResource, \
    TagConcept
from exoset.prerequisite.models import AssignPrerequisiteResource
from exoset.accademic.models import Course
import logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)
# Create your views here.


def right_to_enter_github_section(func):
    # this decorator verifies if the user has the right to enter in the github section of exoset. First verifies if
    # the user has a group otherwise send 401 response. If the user has at least a group assigned, the decorator
    # verifies if the user has a group authorized on an official github repository
    # This decorator has been created for the main page of the github section because a user  can have the rights on
    # more then one github repository
    @login_required()
    def wrapped_func(self, *args, **kwargs):
        user_groups_list = self.user.groups.all()
        user_has_right_to_enter_github_section = False
        list_repositories_names = GitHubRepository.objects.filter(official=True).values_list('repository_name',
                                                                                             flat=True)
        if user_groups_list:
            for group in user_groups_list:
                if group.name in list_repositories_names:
                    user_has_right_to_enter_github_section = True
        else:
            return HttpResponse('Unauthorized', status=401)
        if user_has_right_to_enter_github_section:
            return func(self, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    return wrapped_func


def redirect_user_to_own_repo_list(func):
    # This decorator determines if the user has the right on the specific github repository
    @login_required()
    def wrapped(self, *args, **kwargs):
        if self.user.groups.filter(name=kwargs['github_repo']):
            return func(self, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    return wrapped


def pull_request_restrict(func):
    # To view and accept pull requests the user must be in a specific group and also must be in the group of the
    # specific github repository
    @login_required()
    def wrapper(self, *args, **kwargs):
        if self.user.groups.filter(name=kwargs['github_repo']) and self.user.groups.filter(name='accept_pull_request'):
            return func(self, *args, **kwargs)
        else:
            return HttpResponse('Unauthorized', status=401)
    return wrapper


def new_exercises(github_repo):
    """
    this function returns a list of exercises (folder) which are in the git repository but no Resource instance exists.
    TODO : correct indexError with returning list of existing files/ directories and list of non existing
    """
    try:
        github_repository = GitHubRepository.objects.get(repository_name=github_repo)
    except GitHubRepository.DoesNotExist:
        return None
    path_exercises = settings.MEDIA_ROOT + '/github/' + github_repository.repository_name + '/'
    resourcesourcefile_github_repo = ResourceSourceFile.objects.filter(source__contains=path_exercises)
    try:
        existing_exercises = [x.source.split('/github/' + github_repository.repository_name + '/')[1]
                              for x in resourcesourcefile_github_repo]
        x = set(existing_exercises)
    except IndexError:
        x = None
    ordered_dirs = sorted(os.listdir(path_exercises))
    exercises_from_github = [folder for folder in ordered_dirs if os.path.isdir(path_exercises + folder)]
    y = set(exercises_from_github)
    if x:
        new_exercises_list = y.difference(x)
    else:
        new_exercises_list = y
    if 'cartouche' in new_exercises_list:
        new_exercises_list.remove('cartouche')
    if '.git' in new_exercises_list:
        new_exercises_list.remove('.git')
    if '.github' in new_exercises_list:
        new_exercises_list.remove('.github')
    if '.idea' in new_exercises_list:
        new_exercises_list.remove('.idea')
    if github_repo in new_exercises_list:
        new_exercises_list.remove(github_repo)
    return sorted(new_exercises_list)


@pull_request_restrict
def list_pull_request(request, github_repo):
    """
    this function connect to the github repository registered in the database (more than one repository can exists but
    only one at time can be official). It lists all the pull requests which are opened and passed the tests
    """
    data = {}
    try:
        github_repository = GitHubRepository.objects.get(repository_name=github_repo)
    except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
        return JsonResponse(data, status=200, safe=False)
    g = Github(github_repository.token)
    list_pulls = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).get_pulls(state='all')
    open_pulls = [x for x in list_pulls if x.state == 'open']
    # closed_pulls = [x for x in list_pulls if x.state == 'closed']
    list_open_pulls = {}
    files_changed = ''
    for open_pull in open_pulls:
        verified_pull = True
        commit = list(open_pull.get_commits())[-1]
        for status in commit.get_check_runs():
            if status.name == 'build_latex' and status.conclusion == 'failure':
                verified_pull = False
                break
        if verified_pull:
            for file in open_pull.get_files():
                files_changed = file.filename + ', '
            list_open_pulls[open_pull.number] = _("Pull request posted by {}  on {}. Additional information: {} ; "
                                                  "comments {}; files changed: {}").format(open_pull.user.name,
                                                                                           open_pull.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                                                                                           open_pull.title,
                                                                                           open_pull.comments,
                                                                                           files_changed)
    data['open'] = list_open_pulls

    return render(request, 'list_pull_request.html', {'data': data, 'github_repo': github_repo})


def load_ontology_level1(request):
    root = request.GET.get('root')
    childrens = Ontology.objects.get(pk=root).get_children()
    # children = Ontology.objects.all()
    # nephews = Ontology.objects.all()
    nephews = []
    for x in childrens:
        nephews += x.get_children()
    return render(request, 'children_dropdown_list_options.html', {'childrens': childrens, 'nephews': nephews})


@method_decorator(redirect_user_to_own_repo_list, name='dispatch')
class MetadataFormView(FormView):
    """
    class based function to create / update the metadata of an exercise, in get_context_data the pdf is added in
    context to be shown in the template.
    get_form_kwarg
    pass the id of the resource (if exists) and name of the exercise folder to the form.
    form_valid look for existing resource and metadata updating or creating it
    """
    template_name = 'metadata_form.html'
    form_class = MetadataForm

    def get_context_data(self, **kwargs):
        file_name = self.kwargs['folder_name']
        repository = self.kwargs['github_repo']
        github_repository = GitHubRepository.objects.get(repository_name=repository)
        github_path = settings.MEDIA_ROOT + '/github/' + github_repository.repository_name + '/'
        #enonce_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE.pdf"
        #solution_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE_SOLUTION.pdf"
        #if not os.path.isfile(enonce_pdf):
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE.tex")
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE.tex ; rm *.aux *.log *.aux *.dvi;")
        #if not os.path.isfile(solution_pdf):
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE_SOLUTION.tex")
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE_SOLUTION.tex ; rm *.aux *.log *.aux *.dvi;")
        context = super(MetadataFormView, self).get_context_data()
        context['file_location'] = '/media/github/' + repository + '/' + file_name + "/Compile_" + \
                                   file_name + "_ENONCE_SOLUTION.pdf"
        context['github_repo'] = github_repository.repository_name
        return context

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
        resource_id = self.kwargs['id']
        file_name = self.kwargs['folder_name']
        repository_name = self.kwargs['github_repo']
        logger.info("The user {} modified resource {}".format(self.request.user, file_name))
        # create or update the resource
        try:
            resource = Resource.objects.get(id=int(resource_id))
            resource.title = form.cleaned_data['title']
            resource.language = form.cleaned_data['language']
            resource.author = form.cleaned_data['authors']
            resource.creator = self.request.user
            resource.save()
            message = "The resource {} exists ".format(resource.title)
            logger.info(message)

        except (Resource.DoesNotExist, ValueError):
            resource = Resource.objects.create(title=form.cleaned_data['title'],
                                               language=form.cleaned_data['language'],
                                               author=form.cleaned_data['authors'],
                                               creator=self.request.user
                                               )
            logger.info("the resource has been created")
        # get all the new pdf files, replace the old one or create to Documents objects if it does not exist
        github_path = settings.MEDIA_ROOT + '/github/' + repository_name + '/'
        logger.info('The path of the pdf files created in the github repo is ' + github_path)
        enonce_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE.pdf"
        solution_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE_SOLUTION.pdf"
        try:
            # look for existing statement documents
            new_statement = Document.objects.get(resource=resource, document_type='STATEMENT')
            logger.info("the statement pdf has been found for the resource " + str(resource_id))
        except Document.DoesNotExist:
            new_statement = Document()
            logger.info("the statement pdf has not been created for the resource " + str(resource_id))
        # compile in any case the latex (compiles twice for references to work in latex)
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE.tex")
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE.tex ; rm *.aux *.log *.aux *.dvi;")
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE_SOLUTION.tex")
        os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
                  file_name + "_ENONCE_SOLUTION.tex ; rm *.aux *.log *.aux *.dvi;")
        with open(enonce_pdf, 'rb') as f:
            new_name = update_filename(new_statement, enonce_pdf.split(github_path + file_name)[1])
            new_statement.resource_id = resource.id
            new_statement.document_type = 'STATEMENT'
            new_statement.file.save(new_name, File(f))
        try:
            # look for existing solution documents
            new_solution = Document.objects.get(resource=resource, document_type='SOLUTION')
            logger.info("the solution pdf has been found for the resource " + str(resource_id))
        except Document.DoesNotExist:
            new_solution = Document()
            logger.info("the solution pdf has been created for the resource " + str(resource_id))
        with open(solution_pdf, 'rb') as f:
            new_name_sol = update_filename(new_solution, solution_pdf.split(github_path + file_name)[1])
            new_solution.resource_id = resource.id
            new_solution.document_type = 'SOLUTION'
            new_solution.file.save(new_name_sol, File(f))
        try:
            link_resource_to_code = ResourceSourceFile.objects.get(resource_id=resource.pk)
            link_resource_to_code.source = github_path + file_name
            link_resource_to_code.save()
            logger.info("the ResourceSource file obj has been updated for the resource " + str(resource_id))
        except ResourceSourceFile.DoesNotExist:
            ResourceSourceFile.objects.create(resource=resource, source=github_path+file_name,
                                              style=github_path+'cartouche')
            logger.info("the ResourceSource file obj has been created for the resource " + resource_id)

        data['difficulty_level'] = form.cleaned_data['difficulty_level']
        try:
            taglevelresource = TagLevelResource.objects.get(resource_id=resource.pk)
            taglevelresource.tag_level_id = int(data['difficulty_level'])
            taglevelresource.save()
            logger.info("the TagLevelResource file obj has been updated for the resource " + resource_id)
        except TagLevelResource.DoesNotExist:
            TagLevelResource.objects.create(resource_id=resource.pk, tag_level_id=data['difficulty_level'])
            logger.info("the TagLevelResource file obj has been create for the resource " + str(resource_id))
        data['question_type'] = form.cleaned_data['question_type']
        try:
            question_type_resource = QuestionTypeResource.objects.get(resource_id=resource.pk)
            question_type_resource.question_type_id = data['question_type']
            question_type_resource.save()
            logger.info("the QuestionTypeResource file obj has been updated for the resource " + str(resource_id))
        except QuestionTypeResource.DoesNotExist:
            QuestionTypeResource.objects.create(resource_id=resource.pk, question_type_id=data['question_type'])
            logger.info("the QuestionTypeResource file obj has been created for the resource " + resource_id)
        data['family_problem'] = form.cleaned_data['family_problem']
        try:
            tagproblemtyperesource = TagProblemTypeResource.objects.get(resource_id=resource.pk)
            if data['family_problem']:
                tagproblemtyperesource.tag_problem_type_id = data['family_problem']
                tagproblemtyperesource.save()
                logger.info("the TagProblemTypeResource file obj has been updated for the resource " + str(resource_id))
        except TagProblemTypeResource.DoesNotExist:
            if data['family_problem']:
                tag_problemtype = TagProblemType.objects.create(label=data['family_problem'])
                TagProblemTypeResource.objects.create(resource_id=resource.pk, tag_problem_type_id=tag_problemtype.id)
                logger.info("the TagProblemTypeResource file obj has been created for the resource " + str(resource_id))
        document_categories = DocumentCategory.objects.filter(resource_id=resource.pk)
        data['class_type'] = form.cleaned_data['class_type']
        try:
            course = Course.objects.get(resource__id=resource.pk)
            if not course.sector == data['class_type']:
                course.resource.remove(resource)
                course.save()
                new_course = Course.objects.get(sector=data['class_type'])
                new_course.resource.add(resource)
                new_course.save()
                logger.info("the Course file obj has been changed for the resource " + str(resource_id))
        except Course.DoesNotExist:
            if data['class_type']:
                course = Course.objects.get(sector=data['class_type'])
                course.resource.add(resource)
                course.save()
                logger.info("the Course file obj has been created for the resource " + str(resource_id))
        if document_categories:
            for document_category in document_categories:
                document_category.delete()
        for i in range(2):
            if form.cleaned_data['ontology' + str(i)] != "":
                DocumentCategory.objects.create(resource_id=resource.pk,
                                                category_id=form.cleaned_data['ontology' + str(i)])
        tag_concepts = TagConcept.objects.filter(resource_id=resource.pk)
        for existing_tag_concept in tag_concepts:
            existing_tag_concept.delete()
        prerequisites_resource_exists = AssignPrerequisiteResource.objects.filter(resource_id=resource.pk)
        if prerequisites_resource_exists:
            AssignPrerequisiteResource.objects.get(resource_id=resource.pk).delete()
        for i in range(5):
            if form.cleaned_data['concept' + str(i)] != "":
                TagConcept.objects.create(resource_id=resource.pk, label=form.cleaned_data['concept' + str(i)])
            if form.cleaned_data['prerequisite' + str(i)] != "":
                prerequisite_text = form.cleaned_data['prerequisite' + str(i)]
                print(prerequisite_text[-1:])
                if prerequisite_text[-1:] == ',':
                    prerequisite_text = prerequisite_text[:-1]
                assign_prerequisites_resource, created = AssignPrerequisiteResource.objects.get_or_create(
                    resource_id=resource.pk)
                try:
                    prerequisite = Prerequisite.objects.get(label=prerequisite_text)
                except Prerequisite.DoesNotExist:
                    prerequisite = Prerequisite.objects.create(label=prerequisite_text)
                assign_prerequisites_resource.prerequisite.add(prerequisite)
                assign_prerequisites_resource.save()
        # PUT /repos/{owner}/{repo}/pulls/{pull_number}/merge
        # try:
        #     GitHubRepository.objects.get(official=True)
        # except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
        #     return JsonResponse(data, status=200, safe=False)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        github_repository = self.kwargs['github_repo']
        return reverse('githubadmin:list_resources_files', kwargs={'github_repo': github_repository})


# noinspection PyUnresolvedReferences
@method_decorator(pull_request_restrict, name='dispatch')
class PullRequestDetail(TemplateView):
    template_name = 'pullrequest_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(PullRequestDetail, self).get_context_data(*args, **kwargs)
        data = {}
        try:
            github_repository = GitHubRepository.objects.get(repository_name=context['github_repo'])
        except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
            logger.debug("Error in github repository, Not found.")
            return JsonResponse(data, status=200, safe=False)
        g = Github(github_repository.token)
        logger.info("User " + str(self.request.user) + " access to pull request details for repository " +
                    github_repository.repository_name)
        pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).\
            get_pull(self.kwargs['id'])
        context['pull_request'] = pull_request
        return context


# noinspection PyUnresolvedReferences
@pull_request_restrict
def merge_pull_request(request, pull_request_id, github_repo):
    github_repository = GitHubRepository.objects.get(repository_name=github_repo)
    github_path = settings.MEDIA_ROOT + '/github/' + github_repository.repository_name + '/'
    g = Github(github_repository.token)
    pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).\
        get_pull(pull_request_id)
    logger.info("User " + str(self.request.user) + "tries to accept and merge the pull request " + str(pull_request_id)
                + " for the repository " + str(github_repository.repository_name))
    merge = pull_request.merge()
    if merge:
        # administrator = g.get_user(github_repository.owner)
        # repository = administrator.get_repo(github_repository.repository_name)
        logger.info("User " + str(self.request.user) + " succeded merge ")
        git_local = git.cmd.Git(github_path)
        msg = git_local.pull()
        logger.info("User " + str(self.request.user) + " pulled repository")
        logger.info(msg)
        return HttpResponseRedirect(reverse('githubadmin:list_resources_files',
                                            kwargs={'github_repo': github_repo}))
    else:
        logger.info("Merge failed")
        return render(request, 'error_merge.html')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def prerequisites_autocomplete(request):
    if is_ajax(request=request):
        q = request.GET.get('term', '').capitalize()
        search_qs = list(Prerequisite.objects.filter(label__icontains=q).values('label').distinct())
        concepts_list = [i for i in search_qs]
        data = {
            'tagsconcepts': concepts_list,
        }
        return JsonResponse(data, status=200, safe=False)


def concepts_autocomplete(request):
    if is_ajax(request=request):
        q = request.GET.get('term', '').capitalize()
        graph_url = 'https://graphsearch.epfl.ch/api/search/autocomplete'
        #data = {'field': 'title', 'output': 'props', 'types': 'concept', 'terms': q, 'limit': 30}
        data = {'types': 'concept', 'q': q, 'limit': 30}
        r = requests.get(url=graph_url, params=data)
        r.json()
        search_qs = [x['title'] for x in r.json()['items']]
        data = {
            'tagsconcepts': search_qs,
        }
        return JsonResponse(data, status=200, safe=False)


@method_decorator(redirect_user_to_own_repo_list, name='dispatch')
class ResourceListAdmin(ListView):
    model = ResourceSourceFile
    template_name = 'list_resources_files.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ResourceListAdmin, self).get_context_data(*args, **kwargs)
        github_repository = self.kwargs['github_repo']
        context['new_exercises'] = new_exercises(github_repository)
        context['github_repo'] = github_repository
        logger.info("User " + str(self.request.user) + " access to list of exercises for " +
                    str(self.kwargs['github_repo']) + " repository")
        return context

    def get_queryset(self):
        github_repository = GitHubRepository.objects.get(repository_name=self.kwargs['github_repo'])
        path_exercises = settings.MEDIA_ROOT + '/github/' + github_repository.repository_name + '/'
        return ResourceSourceFile.objects.filter(source__contains=path_exercises)


@redirect_user_to_own_repo_list
def publish_resource(request, github_repo):
    message = ''
    message_missing_field = ''
    user = request.user.username
    if is_ajax(request=request) and request.method == 'POST':
        resource = Resource.objects.get(pk=request.POST.get('id_resource', None))
        form = ResourceForm(request.POST)
        missing_fields = resource.missing_fields_resource
        if missing_fields:
            message_missing_field = _('the resource lacks of {}').format(missing_fields)
        if resource.tag_level:
            resource.visible = request.POST.get('visible', None)
            resource.save()
            published = _('not visible')
            title = resource.title
            if resource.visible == 'True':
                published = _('visible')
            message = str(message_missing_field)
            information_message = _('Success! the exercise {} is {}').format(title, published)
            info_message = "{} changes the visibility of the resource {}".format(user, resource.pk)
            logger.info(info_message)
            return JsonResponse({'success': message, 'information': information_message}, status=200)
        else:
            message = str(message_missing_field) + " " + _('Tag level')
            error_message = "user {} tried to change the resource {} but gives error".format(user, resource)
            logger.info(error_message)
            return JsonResponse({'error': message}, status=400)


@redirect_user_to_own_repo_list
def change_flag_option(request, github_repo):
    user = request.user.username
    message = _("The flag has been changed for the resource")
    if is_ajax(request=request) and request.method == 'POST':
        FlagForm(request.POST)
        resource = Resource.objects.get(pk=request.POST.get('id_resource', None))
        flag = request.POST.get('flag_option', None)
        resource.flag = flag
        resource.save()
        message = "User: " + user + " " + message + " " + resource.title
        logger.info(message)
        return JsonResponse({'success': message}, status=200)


@method_decorator(right_to_enter_github_section, name='dispatch')
class AdminGithub(TemplateView):
    template_name = "repositories_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AdminGithub, self).get_context_data(*args, **kwargs)
        context['list_repositories'] = GitHubRepository.objects.filter(official=True)
        return context
