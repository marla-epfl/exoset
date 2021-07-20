from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils.translation import ugettext_lazy as _

from rest_framework.generics import ListAPIView
from django.views.generic import DetailView
from .models import Resource, Document, LANGUAGES_CHOICES, ResourceSourceFile
from exoset.tag.models import TagConcept, TagLevelResource, TagProblemTypeResource, TagLevel, TagProblemType, \
    QuestionTypeResource
from exoset.accademic.models import Course
from exoset.ontology.models import DocumentCategory, Ontology
from exoset.prerequisite.models import AssignPrerequisiteResource
from .serializers import ResourceSerializers
from .pagination import StandardResultsSetPagination
import os
import zipfile
from io import BytesIO


# Create your views here.
def get_files(request, obj_pk):
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    try:
        resource_source_files_obj = ResourceSourceFile.objects.get(pk=obj_pk)
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
            resource_level = [resource.resource.pk for resource in TagLevelResource.objects.filter(tag_level__label=level)]
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
                                   TagProblemTypeResource.objects.filter(tag_problem_type__label=tag_family)]
            query_list = query_list.filter(id__in=resource_tag_family)
        if course:
            semester = course.split(" : ")
            resource_pk = [resource.pk for resource in
                           Course.objects.get(sector__name__icontains=semester[0], semester=semester[1]).resource.all()]
            query_list = query_list.filter(id__in=resource_pk)
        if language:
            query_list = query_list.filter(language__icontains=language)
        if ontology:
            registered_ontology = DocumentCategory.objects.all()
            resource_pk = []
            ontology = ontology.strip()
            ontology_obj = Ontology.objects.get(name=ontology)
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
        levels_list = [i.label for i in levels]
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
        tag_families_list = [i.label for i in tag_families]
        data = {
            "tag_families": tag_families_list,
        }
        return JsonResponse(data, status=200)


def getCourse(request):
    if request.method == "GET" and request.is_ajax():
        courses = list(Course.objects.all())
        courses_list = [(str(i.sector.name) + " : " + str(i.semester)) for i in courses]
        data = {
            "courses": courses_list,
        }
        return JsonResponse(data, status=200)


def getLanguage(request):
    if request.method == "GET" and request.is_ajax():
        languages = [x[1] for x in LANGUAGES_CHOICES]
        #courses_list = [(str(i.sector.name) + " : " + str(i.semester)) for i in courses]
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

        for child in children:
            ancestors = [x.name for x in child.get_ancestors()]
            ancestors.append(child.name)
            current_child = root_ontology
            for level, ancestor in enumerate(ancestors):
                if ancestor not in current_child.keys():
                    if level == (len(ancestors)-1):
                        current_child[ancestor] = None
                    else:
                        current_child[ancestor] = {}
                else:
                    if current_child[ancestor] is None:
                        if level < (len(ancestors)-1):
                            current_child[ancestor] = {}
                        else:
                            raise NotImplementedError('Duplicate ontology for resource %s'.format(child.name))
                current_child = current_child[ancestor]

        data = {
            "ontologies": root_ontology,
        }
        return JsonResponse(data, status=200)


class ResourceDetailView(DetailView):
    queryset = Resource.objects.filter(visible=True)
    template_name = "resource_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(**kwargs)
        context['documents'] = Document.objects.filter(resource__slug=self.kwargs['slug'])
        context['tag_level'] = TagLevelResource.objects.get(resource__slug=self.kwargs['slug'])
        context['tag_concept'] = TagConcept.objects.filter(resource__slug=self.kwargs['slug'])
        context['problem_type'] = TagProblemTypeResource.objects.filter(resource__slug=self.kwargs['slug']).\
            select_related('tag_problem_type')
        context['courses'] = Course.objects.filter(resource__slug=self.kwargs['slug']).select_related('sector')
        context['ontology'] = DocumentCategory.objects.filter(resource__slug=self.kwargs['slug'])
        try:
            context['prerequisites'] = AssignPrerequisiteResource.objects.get(resource__slug=self.kwargs['slug'])
        except AssignPrerequisiteResource.DoesNotExist:
            context['prerequisites'] = ""
        try:
            context['question_type'] = QuestionTypeResource.objects.get(resource__slug=self.kwargs['slug'])
        except QuestionTypeResource.DoesNotExist:
            context['question_type'] = ""
        return context
