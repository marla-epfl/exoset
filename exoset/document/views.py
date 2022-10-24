from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.core.exceptions import MultipleObjectsReturned
from rest_framework.generics import ListAPIView
from django.views.generic import DetailView, ListView
from .models import Resource, Document, LANGUAGES_CHOICES, ResourceSourceFile
from exoset.tag.models import TagConcept, TagLevelResource, TagProblemTypeResource, TagLevel, TagProblemType, \
    QuestionTypeResource
from exoset.accademic.models import Course, Sector
from exoset.ontology.models import DocumentCategory, Ontology
from exoset.prerequisite.models import AssignPrerequisiteResource
from .serializers import ResourceSerializers
from .pagination import StandardResultsSetPagination
import os
import zipfile
from io import BytesIO
import logging
import urllib.parse

logger = logging.getLogger(__name__)

# Create your views here.
def get_files(request, obj_pk):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    try:
        resource_source_files_obj = ResourceSourceFile.objects.get(resource_id=obj_pk)
    except ResourceSourceFile.DoesNotExist:
        msg = _("Sorry, there was a problem with the file, please contact us")
        resp = HttpResponse(msg, content_type='text/plain')
        return resp
    path = resource_source_files_obj.source
    path_style = resource_source_files_obj.style
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_subdir = "exercise"
    zip_filename = "%s.zip" % zip_subdir
    # Open StringIO to grab in-memory ZIP contents
    s = BytesIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")
    for root, dirs, files in os.walk(path):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    for root, dirs, files in os.walk(path_style):
        for file in files:
            zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path_style, '..')))
    zf.close()
    user = request.user
    if 'teacher' in user.groups.values_list('name', flat=True):
        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    else:
        msg = _("You have no rights to download this file")
        resp = HttpResponse(msg, content_type='text/plain')
    return resp


def ResourceList(request):
    return render(request, "resources.html", {})


class ResourceListing(ListAPIView):
    # set the pagination and serializer class
    pagination_class = StandardResultsSetPagination
    serializer_class = ResourceSerializers

    def get_queryset(self):
        # filter the queryset based on the filters applied

        query_list = Resource.objects.filter(visible=True)
        author = self.request.query_params.get('author', None)
        level = self.request.query_params.get('level', None)
        tag_concept = self.request.query_params.get('concept', None)
        tag_family = self.request.query_params.get('tagproblemtype', None)
        course = self.request.query_params.get('course', None)
        language = self.request.query_params.get('language', None)
        ontology = self.request.query_params.get('ontology', None)
        if author:
            query_list = query_list.filter(author=author)
        if level:
            resource_level = [resource.resource.pk for resource in TagLevelResource.objects.filter(tag_level_id=level)]
            query_list = query_list.filter(id__in=resource_level)
        if tag_concept:
            tags = list(filter(None, tag_concept.split(", ")))
            # Or logic
            # resources_with_tag_concept = [resource.resource.pk for resource in
            #                              TagConcept.objects.filter(label__in=tags)]
            # AND logic
            resources_with_tag_concept = [resource.resource.pk for resource in TagConcept.objects.filter(label=tags[0])]
            # new_resource_with_tag_concept = []
            # for tag in range(1, len(tags)):
            #    new_tag = TagConcept.objects.filter(label=tags[tag])
            #    new_resource_with_tag_concept.append([resource.resource.pk for resource in new_tag])
            # if new_resource_with_tag_concept:
            #   resources_with_tag_concept = set(new_resource_with_tag_concept).intersection(resources_with_tag_concept)
            query_list = query_list.filter(id__in=resources_with_tag_concept)
        if tag_family:
            resource_tag_family = [resource.resource.pk for resource in
                                   TagProblemTypeResource.objects.filter(tag_problem_type_id=tag_family)]
            query_list = query_list.filter(id__in=resource_tag_family)
        if course:
            semester = course
            resource_pk = [resource.pk for resource in
                           Course.objects.get(id=semester).resource.all()]
            query_list = query_list.filter(id__in=resource_pk)
        if language:
            query_list = query_list.filter(language__icontains=language)
        if ontology:
            registered_ontology = DocumentCategory.objects.all()
            resource_pk = []
            ontology = ontology.strip()
            ontology_obj = Ontology.objects.get(pk=ontology)
            for doc in registered_ontology:
                if doc.category == ontology_obj or ontology_obj in doc.ontology_tree():
                    resource_pk.append(doc.resource.pk)
            query_list = query_list.filter(id__in=resource_pk)
        return query_list


def getAuthors(request):
    # get all the authors from the database excluding
    # null and blank values

    if request.method == "GET" and request.is_ajax():
        authors = Resource.objects.exclude(author__isnull=True).exclude(author__exact='').order_by('author').\
            values_list('author').distinct()
        authors_list = [i[0] for i in list(authors)]
        data = {
            "authors": authors_list,
        }
        return JsonResponse(data, status=200)


def getLevel(request):
    # get all the levels from the database excluding
    # null and blank values

    if request.method == "GET" and request.is_ajax():
        levels = list(TagLevel.objects.all())
        levels_list = [(i.label, i.pk) for i in levels]
        data = {
            "levels": levels_list,
        }
        return JsonResponse(data, status=200)


def getTagConcept(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        search_qs = list(TagConcept.objects.filter(label__icontains=q).values('label').distinct())
        concepts_list = [i for i in search_qs]
        data = {
            'tagsconcepts': concepts_list,
        }
        return JsonResponse(data, status=200, safe=False)


def getTagFamily(request):
    if request.method == "GET" and request.is_ajax():
        tag_families = list(TagProblemType.objects.all())
        tag_families_list = [(i.label, i.pk) for i in tag_families]
        data = {
            "tag_families": tag_families_list,
        }
        return JsonResponse(data, status=200)


def getCourse(request):
    if request.method == "GET" and request.is_ajax():
        courses = list(Course.objects.all())
        courses_list = [(i.sector.name, i.pk) for i in courses]
        data = {
            "courses": courses_list,

        }
        return JsonResponse(data, status=200)


def getLanguage(request):
    if request.method == "GET" and request.is_ajax():
        languages = [x[1] for x in LANGUAGES_CHOICES]
        # courses_list = [(str(i.sector.name) + " : " + str(i.semester)) for i in courses]
        data = {
            "languages": languages,
        }
        return JsonResponse(data, status=200)


def getOntology(request):
    if request.method == 'GET' and request.is_ajax():
        distinct_branches = DocumentCategory.objects.all().select_related('category').values('category').\
            distinct().values_list('category_id', flat=True)
        children = [x for x in Ontology.objects.all() if x.pk in distinct_branches]
        root_ontology = {}
        #root_ontology_pks = {}
        current_child_pks = []
        for child in children:
            ancestors = [x.name for x in child.get_ancestors()]
            ancestors_pks = [x.pk for x in child.get_ancestors()]
            ancestors.append(child.name)
            ancestors_pks.append(child.pk)
            current_child = root_ontology
            #current_child_pks = root_ontology_pks
            for level, ancestor in enumerate(ancestors):
                if ancestor not in current_child.keys():
                    if level == (len(ancestors)-1):
                        current_child[ancestor] = None
                        #current_child_pks[ancestors_pks[level]] = None
                        current_child_pks.append(ancestors_pks[level])
                    else:
                        current_child[ancestor] = {}
                        #current_child_pks[ancestors_pks[level]] = {}
                        current_child_pks.append(ancestors_pks[level])
                else:
                    if current_child[ancestor] is None:
                        if level < (len(ancestors)-1):
                            current_child[ancestor] = {}
                            #current_child_pks[ancestors_pks[level]] = {}
                            current_child_pks.append(ancestors_pks[level])
                        else:
                            raise NotImplementedError('Duplicate ontology for resource {}'.format(child.name))
                current_child = current_child[ancestor]
                #current_child_pks = current_child_pks[ancestors_pks[level]]

        data = {
            "ontologies": root_ontology,
            "ontologies_pk": current_child_pks,
        }

        return JsonResponse(data, status=200)


class ResourceDetailView(DetailView):
    queryset = Resource.objects.filter(visible=True)
    template_name = "resource_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(**kwargs)
        documents = Document.objects.filter(resource__slug=self.kwargs['slug'])
        context['statement'] = documents.filter(document_type='STATEMENT')[0]
        context['solution'] = documents.filter(document_type='SOLUTION')[0]
        roots_list = Ontology.get_root_nodes().values_list('name', flat=True)
        context['list_parent_ontology'] = roots_list
        context['ontology'] = DocumentCategory.objects.filter(resource__slug=self.kwargs['slug'])
        if 'HTTP_REFERER' in self.request.META:
            previous_link = self.request.META['HTTP_REFERER'].split('resources/')
            try:
                if '?' in previous_link[1]:
                    metadata = previous_link[1].split('?')
                    metadata = metadata[0].split('/')
                else:
                    metadata = previous_link[1].split('/')
                i = 1
                for ontology in metadata:
                    if ontology != self.kwargs['slug']:
                        context['breadcrumb' + str(i)] = urllib.parse.unquote(mark_safe(ontology))
                        i += 1
            except IndexError:
                print("redirection without filters")
        message = 'the {} exercise has been seen'.format(self.kwargs['slug'])
        logger.info(message + '\n')
        return context


class ExercisesList(ListView):
    model = Resource
    template_name = 'resource_list.html'
    paginate_by = 10

    def get_queryset(self):
        """
        this view should return the list of all the exercises filtered by a specific ontology main class (Math or
        Physics)
        """
        # search for the right ontology branch to set the right search
        ontology_parent_parameter = None
        list_resources = Resource.objects.filter(visible=True)
        message = 'Search for ontology '
        if 'ontologyRoot' in self.kwargs and self.kwargs['ontologyRoot']:
            ontology_parent_parameter = self.kwargs['ontologyRoot']
            message += '{} -'.format(ontology_parent_parameter)
        message = ""
        if 'ontologyParent' in self.kwargs and self.kwargs['ontologyParent']:
            ontology_parent_parameter = self.kwargs['ontologyParent']
            message += '{} -'.format(ontology_parent_parameter)
        if 'ontologyChild' in self.kwargs and self.kwargs['ontologyChild']:
            ontology_parent_parameter = self.kwargs['ontologyChild']
            message += '{} -'.format(ontology_parent_parameter)
        if "difficulty" in self.request.GET:
            difficulty = self.request.GET.getlist("difficulty")
            resources_filtered_by_level = [resource.resource.pk for resource in
                              TagLevelResource.objects.filter(tag_level_id__in=difficulty)]
            list_resources = list_resources.filter(id__in=resources_filtered_by_level)
            message += '. Difficulty filter: {}; '.format(str(difficulty))
        if "course" in self.request.GET:
            course_pk = self.request.GET.get("course")
            resources_filtered_by_study_program = [resource.pk for resource in Course.objects.get(id=course_pk).resource.all()]
            list_resources = list_resources.filter(id__in=resources_filtered_by_study_program)
            message += '. Course filter: {}; '.format(str(course_pk))
        if "language" in self.request.GET:
            languages = self.request.GET.getlist("language")
            list_resources = list_resources.filter(language__in=languages)
        try:
            ontology_parent = Ontology.objects.get(name=ontology_parent_parameter)
        except (Ontology.MultipleObjectsReturned, Ontology.DoesNotExist):
            logger.warning("The ontology {} return more than one object".format(ontology_parent_parameter))
            return list_resources
        if 'ontologyChild' in self.kwargs:
            ontology_child_pk = ontology_parent.id
            list_resources_pks = DocumentCategory.objects.filter(category_id=ontology_child_pk). \
                values_list('resource_id', flat=True)
        else:
            list_ontology_branches_pks = ontology_parent.get_descendants().values_list('id', flat=True)
            list_resources_pks = DocumentCategory.objects.filter(category_id__in=list_ontology_branches_pks).\
                values_list('resource_id', flat=True)
        if list_resources_pks:
            list_resources = list_resources.filter(id__in=list_resources_pks, visible=True)
        else:
            list_resources = []
        logger.info(message + '\n')
        return list_resources

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roots_list = Ontology.get_root_nodes().values_list('name', flat=True)
        context['list_parent_ontology'] = roots_list
        list_menu = []
        for root in roots_list:
            if 'ontologyRoot' in self.kwargs and root == self.kwargs['ontologyRoot']:
                list_menu.append("current-menu-item")
            else:
                list_menu.append("")
        context['root'] = True
        context['parent'] = False
        context['child'] = False
        if 'ontologyRoot' in self.kwargs:
            context['root_ontology_filter'] = urllib.parse.unquote(self.kwargs['ontologyRoot'])
            root = Ontology.objects.get(name=urllib.parse.unquote(self.kwargs['ontologyRoot']))
            context['ontology_list_left_menu'] = root.get_children().values_list('name', flat=True)
            if 'ontologyParent' in self.kwargs:
                context['parent_ontology_filter'] = urllib.parse.unquote(self.kwargs['ontologyParent'])
                parent = Ontology.objects.get(name=urllib.parse.unquote(self.kwargs['ontologyParent']))
                context['ontology_list_left_menu'] = parent.get_children().values_list('name', flat=True)
                context['root'] = False
                context['parent'] = True
                context['child'] = False
                if 'ontologyChild' in self.kwargs:
                    context['child_ontology_filter'] = urllib.parse.unquote(self.kwargs['ontologyChild'])
                    context['ontology_list_left_menu'] = parent.get_children().values_list('name', flat=True)
                    context['root'] = False
                    context['parent'] = False
                    context['child'] = True
        else:
            context['root_ontology_filter'] = ""
            context['ontology_list_left_menu'] = roots_list
        context['difficulties_list'] = TagLevel.objects.all()
        context['languages_list'] = LANGUAGES_CHOICES
        context['courses_list'] = Sector.objects.all()
        if 'difficulty' in self.request.GET:
            context['difficulties_selected'] = [int(x) for x in self.request.GET.getlist('difficulty')]
        if 'course' in self.request.GET:
            context['course_selected'] = int(self.request.GET.get('course'))
        if 'language' in self.request.GET:
            context['languages_selected'] = [x for x in self.request.GET.getlist('language')]
        return context

