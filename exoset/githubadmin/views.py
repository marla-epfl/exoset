from django.shortcuts import render, get_object_or_404
from github import Github
from django.http import JsonResponse
import git
import os
import subprocess
import requests
from .models import GitHubRepository
from django.core.exceptions import MultipleObjectsReturned
from django.core.files.base import File
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import MetadataForm, ResourceForm, FlagForm
from django.utils.translation import ugettext_lazy as _
from exoset.prerequisite.models import Prerequisite
from exoset.document.models import Resource, ResourceSourceFile, Document, update_filename
from exoset.ontology.models import Ontology, DocumentCategory
from exoset.tag.models import TagLevelResource, TagProblemTypeResource, TagProblemType, QuestionTypeResource, \
    TagConcept
from exoset.prerequisite.models import AssignPrerequisiteResource
from exoset.accademic.models import Course
# Create your views here.


def new_exercises():
    """
    this function returns a list of exercises (folder) which are in the git repository but no Resource instance exists.
    TODO : correct indexError with returning list of existing files/ directories and list of non existing
    """

    path_exercises = settings.MEDIA_ROOT + '/github/' + settings.GITHUB_REPO_NAME + '/'
    try:
        existing_exercises = [x.source.split('/github/' + settings.GITHUB_REPO_NAME + '/')[1]
                              for x in ResourceSourceFile.objects.all()]
        x = set(existing_exercises)
    except IndexError:
        x = None
    exercises_from_github = [folder for folder in os.listdir(path_exercises) if os.path.isdir(path_exercises + folder)]
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
    if settings.GITHUB_REPO_NAME in new_exercises_list:
        new_exercises_list.remove(settings.GITHUB_REPO_NAME)
    return new_exercises_list


def list_pull_request(request):
    """
    this function connect to the github repository registered in the database (more than one repository can exists but
    only one at time can be official). It lists all the pull requests which are opened and passed the tests
    """
    data = {}
    try:
        github_repository = GitHubRepository.objects.get(official=True)
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

    return render(request, 'list_pull_request.html', {'data': data})


def load_ontology_level1(request):
    root = request.GET.get('root')
    childrens = Ontology.objects.get(pk=root).get_children()
    #children = Ontology.objects.all()
    #nephews = Ontology.objects.all()
    nephews = []
    for x in childrens:
        nephews += x.get_children()
    print(nephews)
    print(childrens)
    return render(request, 'children_dropdown_list_options.html', {'childrens': childrens, 'nephews':nephews})


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
        github_path = settings.MEDIA_ROOT + '/github/' + settings.GITHUB_REPO_NAME + '/'
        enonce_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE.pdf"
        solution_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE_SOLUTION.pdf"
        if not os.path.isfile(enonce_pdf):
            os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE.tex")
            os.system(
                "cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE.tex ; rm *.aux *.log *.aux *.dvi;")
        if not os.path.isfile(solution_pdf):
            os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE_SOLUTION.tex")
            os.system(
                "cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE_SOLUTION.tex ; rm *.aux *.log *.aux *.dvi;")
        context = super(MetadataFormView, self).get_context_data()
        context['file_location'] = '/media/github/' + settings.GITHUB_REPO_NAME + '/' + file_name + "/Compile_" + file_name + "_ENONCE_SOLUTION.pdf"
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
        # create or update the resource
        try:
            resource = Resource.objects.get(id=int(resource_id))
            print(_("The resource {} exists ").format(resource.title))
        except (Resource.DoesNotExist, ValueError):
            resource = Resource.objects.create(title=form.cleaned_data['title'],
                                               language=form.cleaned_data['language'],
                                               author=form.cleaned_data['authors'],
                                               creator=self.request.user
                                               )
            print("the resource has been created")
        # get all the new pdf files, replace the old one or create to Documents objects if it does not exist
        github_path = settings.MEDIA_ROOT + '/github/' + settings.GITHUB_REPO_NAME + '/'
        print("the github path in metadata creation is " + github_path)
        enonce_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE.pdf"
        solution_pdf = github_path + file_name + "/Compile_" + file_name + "_ENONCE_SOLUTION.pdf"
        try:
            new_statement = Document.objects.get(resource=resource, document_type=Document.STAT)
            print("the statement pdf file has been updated")
        except Document.DoesNotExist:
            new_statement = Document()
        # check if pdf exist:
        enonce = soluzione = 0
        if not os.path.isfile(enonce_pdf):
            enonce = os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE.tex")
        if not os.path.isfile(solution_pdf):
            soluzione = os.system("cd " + github_path + file_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" + file_name + "_ENONCE_SOLUTION.tex")
        if (enonce + soluzione) > 0:
            return JsonResponse(data, status=400, safe=False)
        with open(enonce_pdf, 'rb') as f:
            new_name = update_filename(new_statement, enonce_pdf.split(github_path + file_name)[1])
            new_statement.resource_id = resource.id
            new_statement.document_type = Document.STAT
            new_statement.file.save(new_name, File(f))
        print("the statement pdf file has been created")

        try:
            new_solution = Document.objects.get(resource=resource, document_type=Document.SOL)
            print("the solution pdf file has been updated")
        except Document.DoesNotExist:
            new_solution = Document()
        with open(solution_pdf, 'rb') as f:
            new_name_sol = update_filename(new_solution, solution_pdf.split(github_path + file_name)[1])
            new_solution.resource_id = resource.id
            new_solution.document_type = Document.SOL
            new_solution.file.save(new_name_sol, File(f))
        try:
            link_resource_to_code = ResourceSourceFile.objects.get(resource_id=resource.pk)
            link_resource_to_code.source = github_path + file_name
            link_resource_to_code.save()
            print("the ResourceSource file obj has been updated")
        except ResourceSourceFile.DoesNotExist:
            ResourceSourceFile.objects.create(resource=resource, source=github_path+file_name,
                                              style=github_path+'cartouche')
            print("the ResourceSource file obj has been created")

        data['difficulty_level'] = form.cleaned_data['difficulty_level']
        try:
            taglevelresource = TagLevelResource.objects.get(resource_id=resource.pk)
            taglevelresource.tag_level.id = data['difficulty_level']
            taglevelresource.save()
        except TagLevelResource.DoesNotExist:
            TagLevelResource.objects.create(resource_id=resource.pk, tag_level_id=data['difficulty_level'])
        data['question_type'] = form.cleaned_data['question_type']
        try:
            question_type_resource = QuestionTypeResource.objects.get(resource_id=resource.pk)
            question_type_resource.question_type.id = data['question_type']
            question_type_resource.save()
        except QuestionTypeResource.DoesNotExist:
            QuestionTypeResource.objects.create(resource_id=resource.pk, question_type_id=data['question_type'])
        data['family_problem'] = form.cleaned_data['family_problem']
        try:
            tagproblemtyperesource = TagProblemTypeResource.objects.get(resource_id=resource.pk)
            tagproblemtyperesource.tag_problem_type.id = data['family_problem']
            tagproblemtyperesource.save()
        except TagProblemTypeResource.DoesNotExist:
            tag_problemtype = TagProblemType.objects.create(label=data['family_problem'])
            TagProblemTypeResource.objects.create(resource_id=resource.pk, tag_problem_type_id=tag_problemtype.id)
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
        except Course.DoesNotExist:
            if data['class_type']:
                course = Course.objects.get(sector=data['class_type'])
                course.resource.add(resource)
                course.save()
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
        try:
            github_repository = GitHubRepository.objects.get(official=True)
        except (GitHubRepository.DoesNotExist, MultipleObjectsReturned):
            return JsonResponse(data, status=200, safe=False)

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('githubadmin:list_resources_files')


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
        pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).\
            get_pull(self.kwargs['id'])
        context['pull_request'] = pull_request
        return context


def merge_pull_request(request, pull_request_id):
    github_repository = GitHubRepository.objects.get(official=True)
    github_path = settings.MEDIA_ROOT + '/github/' + settings.GITHUB_REPO_NAME + '/'
    g = Github(github_repository.token)
    pull_request = g.get_user(github_repository.owner).get_repo(github_repository.repository_name).\
        get_pull(pull_request_id)
    merge = pull_request.merge()
    if merge:
        administrator = g.get_user(github_repository.owner)
        repository = administrator.get_repo(github_repository.repository_name)
        git_local = git.cmd.Git(github_path)
        msg = git_local.pull()
        print(msg)
        return HttpResponseRedirect(reverse('githubadmin:list_resources_files'))
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


def concepts_autocomplete(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        graph_url = 'https://graphsearch.epfl.ch/api/search'
        data = {'field': 'title', 'output': 'props', 'types': 'concept', 'terms': q, 'size': 30}
        r = requests.post(url=graph_url, json=data)
        r.json()
        search_qs = [x['title'] for x in r.json()['docs']]
        data = {
            'tagsconcepts': search_qs,
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


def publish_resource(request):
    message = ''
    message_missing_field = ''
    if request.is_ajax and request.method == 'POST':
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
            # print("the resource {} is now visible").format(resource.pk)
            return JsonResponse({'success': message, 'information': information_message}, status=200)
        else:
            message = str(message_missing_field) + " " + _('Tag level')
            print("the resource {} gives error").format(resource)
            return JsonResponse({'error': message}, status=400)


def change_flag_option(request):
    message = _("The flag has been changed for the resource")
    if request.is_ajax and request.method == 'POST':
        FlagForm(request.POST)
        resource = Resource.objects.get(pk=request.POST.get('id_resource', None))
        flag = request.POST.get('flag_option', None)
        resource.flag = flag
        resource.save()
        message = message + " " + resource.title
        return JsonResponse({'success': message}, status=200)
