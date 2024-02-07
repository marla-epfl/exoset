from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.db.models import Q
from django.utils.translation import override
from django.views.generic import DetailView, ListView, TemplateView
from .models import Resource, Document, LANGUAGES_CHOICES, ResourceSourceFile
from exoset.tag.models import TagConcept, TagLevelResource, TagLevel
from exoset.accademic.models import Course, Sector
from exoset.ontology.models import DocumentCategory, Ontology
from datetime import datetime
import os
import zipfile
from io import BytesIO
import logging
import urllib.parse
from unidecode import unidecode
from collections import OrderedDict
from django.conf import settings

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
    print('resource style path is : ' + str(path_style))
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
            print(file)
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


def getTagConcept(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        search_qs = list(TagConcept.objects.filter(label__icontains=q).values('label').distinct())
        concepts_list = [i for i in search_qs]
        data = {
            'tagsconcepts': concepts_list,
        }
        return JsonResponse(data, status=200, safe=False)


def create_zip(zip_object, path, path_style):
    for (root, dirs, filenames) in os.walk(path):
        for file in filenames:
            zip_object.write(os.path.join(root, file),
                             os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    for (root, dirs, filenames) in os.walk(path_style):
        for file in filenames:
            zip_object.write(os.path.join(root, file),
                             os.path.relpath(os.path.join(root, file), os.path.join(path_style, '..')))
    return zip_object


def overleaf_link(request, slug):
    from zipfile import ZipFile
    result = ""
    resurcesourcefile_obj = ResourceSourceFile.objects.get(resource__slug=slug)
    path = resurcesourcefile_obj.source
    path_style = resurcesourcefile_obj.style
    if not os.path.exists(settings.MEDIA_ROOT + '/overleaf'):
        os.makedirs(settings.MEDIA_ROOT + '/overleaf')
    path_tmp = settings.MEDIA_ROOT + '/overleaf/' + resurcesourcefile_obj.resource.slug + '.zip'
    #TODO add cartouche with folder
    if os.path.exists(path_tmp):
        result = path_tmp
    else:
        zip_object = ZipFile(path_tmp, 'w')
        create_zip(zip_object, path, path_style)
        zip_object.close()
        result = path_tmp
    overleaf_url = 'https://www.overleaf.com/docs?snip_uri[]=' + settings.DOMAIN_NAME + settings.MEDIA_URL + \
                   result.split(settings.MEDIA_URL)[1]
    #print(overleaf_url)
    return HttpResponseRedirect(overleaf_url)


def build_zip_series(id_list):
    result = ""
    id_list = id_list.split(',')
    series_name = str(datetime.now().timestamp())
    if not os.path.exists(settings.MEDIA_ROOT + '/overleaf'):
        os.makedirs(settings.MEDIA_ROOT + '/overleaf')
    path_tmp = settings.MEDIA_ROOT + '/overleaf/' + series_name + '.zip'
    path_style = settings.MEDIA_ROOT + '/overleaf/cartouche'
    initial_common_text = "\documentclass[12pt,dvipsnames]{article}\n\input{cartouche/generic/preamble}\n\n" \
                          "\\begin{document}\n \\begin{center}\n \\vspace*{10mm}\n \\noindent {\Large {\\bf Series}} \n " \
                          "\end{center}\n "
    begin_enumerate = '\\begin{enumerate}\n'
    solution_common_text = '\\begin{center}\n \\vspace*{5mm} \n \\noindent \end{center}\n '
    end_document = '\n\input{cartouche/generic/cartouche}\n \end{document}\n'
    statement_text = ''
    solution_text = ''
    end_enumerate = '\n \end{enumerate}\n'
    figure_path = '\\graphicspath{'
    with zipfile.ZipFile(path_tmp, 'w') as zip_object:
        i = 1
        for id in id_list:
            try:
                resurcesourcefile_obj = ResourceSourceFile.objects.get(resource__id=int(id))
                path = resurcesourcefile_obj.source
                path_style = resurcesourcefile_obj.style
                statement_text += '\item[' + str(i) + ')]\n' + '\input{' + path.rsplit('/')[-1] + '/' + path.rsplit('/')[-1] + '_E}]\n'
                solution_text += '\item[' + str(i) + ')]\n' + '\input{' + path.rsplit('/')[-1] + '/' + path.rsplit('/')[-1] + '_E}]\n' + '\input{' + path.rsplit('/')[-1] + '/' + path.rsplit('/')[-1] + '_S}\n'
                figure_path += '{' + path.rsplit('/')[-1] + '}'
                i += 1
            except ResourceSourceFile.DoesNotExist:
                continue
            create_zip(zip_object, path, path_style)
        # create compile file for statements
        statement_common_text = initial_common_text + figure_path + '}' + begin_enumerate + statement_text + end_enumerate
        solution_final_text = initial_common_text + figure_path + '}' + solution_common_text + begin_enumerate + solution_text + end_enumerate + end_document
        statement_common_text += end_document
        series_statement_path = settings.MEDIA_ROOT + '/overleaf/compile_series_statement.tex'
        series_solution_path = settings.MEDIA_ROOT + '/overleaf/compile_series_solution.tex'
        with open(series_statement_path, 'a') as statement:
            statement.write(statement_common_text)
            statement.close()
        # create compile file for solution
        with open(series_solution_path, 'a') as solution:
            solution.write(solution_final_text)
            solution.close()
        #add compile files to zip
        zip_object.write(series_statement_path, os.path.basename(series_statement_path))
        zip_object.write(series_solution_path, os.path.basename(series_solution_path))
        zip_object.close()
    result = path_tmp
    return series_statement_path, series_solution_path, result


def download_pdf(request, id_list=''):
    zip_file = build_zip_series(id_list)
    file_path = os.path.join(settings.MEDIA_ROOT, zip_file[2])
    new_folder = os.path.join(settings.MEDIA_ROOT, 'exercise_pdf')
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(new_folder)
    try:
        os.system(
            "cd " + new_folder + " ; pdflatex -interaction=nonstopmode -halt-on-error compile_series_solution.tex")
        os.system(
            "cd " + new_folder + " ; pdflatex -interaction=nonstopmode -halt-on-error compile_series_solution.tex")
        with open('compile_series_solution.pdf', 'rb') as pdf_file:
            resp = HttpResponse(pdf_file.read(), content_type="application/pdf")
            resp['Content-Disposition'] = 'attachment; filename=%s' % 'series_solution.pdf'
            try:
                os.rmdir(new_folder)
                os.remove(file_path)
            except OSError as e:
                # If it fails, inform the user.
                print("Error: %s - %s." % (e.filename, e.strerror))
            return resp
    except:
        try:
            os.rmdir(new_folder)
            os.rmdir(file_path)
        except OSError as e:
            # If it fails, inform the user.
            print("Error: %s - %s." % (e.filename, e.strerror))
        msg = _("Sorry, there was a problem")
        resp = HttpResponse(msg, content_type='text/plain')
        return resp


def download_series(request, id_list=''):
    zip_file = build_zip_series(id_list)
    file_path = os.path.join(settings.MEDIA_ROOT, zip_file[2])
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/x-zip-compressed")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            try:
                # remove existing files for compiling series
                os.remove(zip_file[0])
                os.remove(zip_file[1])
            except OSError as e:
                # If it fails, inform the user.
                print("Error: %s - %s." % (e.filename, e.strerror))
            return response
    raise Http404


def overleaf_link_series(request, id_list):
    zip_file = build_zip_series(id_list)
    overleaf_url = 'https://www.overleaf.com/docs?snip_uri[]=' + settings.DOMAIN_NAME + settings.MEDIA_URL + \
                   zip_file[2].split(settings.MEDIA_URL)[1]
    try:
        # remove existing files for compiling series
        os.remove(zip_file[0])
        os.remove(zip_file[1])
    except OSError as e:
        # If it fails, inform the user.
        print("Error: %s - %s." % (e.filename, e.strerror))
    return HttpResponseRedirect(overleaf_url)


class ResourceDetailView(DetailView):
    queryset = Resource.objects.filter(visible=True)
    template_name = "resource_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ResourceDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous:
            user = "anonymous"
            context['add_cart'] = mark_safe('style=float:right;margin-top:-10px; title="you must log in" disabled')
        else:
            user = self.request.user.username
            context['add_cart'] = mark_safe("style=float:right;margin-top:-10px;background-color:transparent;color:#ff0000")
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
        message = 'User {} looked at the {} exercise'.format(user, self.kwargs['slug'])
        logger.info(message + '\n')
        if 'cart' in self.request.session.keys():
            context['exercises_number'] = len(self.request.session['cart'])
            cart = list(Cart(self.request)).__iter__()

            context['cart_view'] = cart
            context['exercises_ids'] = ','.join(list(self.request.session['cart'].keys()))
        else:
            context['exercises_ids'] = ''
            context['exercises_number'] = 0
            context['cart_view'] = {}
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
        query_search_form = self.request.GET.get("search")
        ontology_parent_parameter = None
        list_resources = Resource.objects.filter(visible=True)
        if self.request.user:
            user = self.request.user.username
        else:
            user = "anonymous"
        if query_search_form:
            concept_search = [resource.resource.pk for resource in
                              TagConcept.objects.filter(label__icontains=query_search_form)]
            list_resources = list_resources.filter(Q(title__icontains=query_search_form) |
                                               Q(author__icontains=query_search_form) | Q(id__in=concept_search))
        if 'ontologyRoot' in self.kwargs and self.kwargs['ontologyRoot']:
            ontology_parent_parameter = self.kwargs['ontologyRoot']
        if 'ontologyParent' in self.kwargs and self.kwargs['ontologyParent']:
            ontology_parent_parameter = self.kwargs['ontologyParent']
        if 'ontologyChild' in self.kwargs and self.kwargs['ontologyChild']:
            ontology_parent_parameter = self.kwargs['ontologyChild']
        if "difficulty" in self.request.GET:
            difficulty = self.request.GET.getlist("difficulty")
            resources_filtered_by_level = [resource.resource.pk for resource in
                              TagLevelResource.objects.filter(tag_level_id__in=difficulty)]
            list_resources = list_resources.filter(id__in=resources_filtered_by_level)
        if "course" in self.request.GET:
            course_pk = self.request.GET.get("course")
            resources_filtered_by_study_program = [resource.pk for resource in Course.objects.get(id=course_pk).resource.all()]
            list_resources = list_resources.filter(id__in=resources_filtered_by_study_program)
        if "language" in self.request.GET:
            languages = self.request.GET.getlist("language")
            list_resources = list_resources.filter(language__in=languages)
        try:
            ontology_parent = Ontology.objects.get(name=ontology_parent_parameter)
        except (Ontology.MultipleObjectsReturned, Ontology.DoesNotExist):
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
        return list_resources

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roots_list = Ontology.get_root_nodes().values_list('name', flat=True)
        context['list_parent_ontology'] = roots_list
        if 'cart' in self.request.session.keys():
            context['exercises_number'] = len(self.request.session['cart'])
        else:
            context['exercises_number'] = 0
        list_menu = []
        if self.request.user.is_anonymous:
            user = "anonymous"
            context['add_cart'] = mark_safe('style=float:right;margin-top:-10px; title="you must log in" disabled')
        else:
            user = self.request.user.username
            context['add_cart'] = mark_safe("style=float:right;margin-top:-10px;background-color:transparent;color:#ff0000")
        message = "User {} ".format(user)
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
            message += "search for ontology {}".format(context['root_ontology_filter'])
            root = Ontology.objects.get(name=urllib.parse.unquote(self.kwargs['ontologyRoot']))
            list_ontology_second_level = sorted(root.get_children(), key=lambda x: unidecode(x.name.lower()))
            context['ontology_list_left_menu'] = OrderedDict()
            for x in list_ontology_second_level:
                trans = x.name
                with override('en'):
                    context['ontology_list_left_menu'][x.name] = trans
            #context['ontology_list_left_menu'] = root.get_children().values_list('name', flat=True)
            if 'ontologyParent' in self.kwargs:
                context['parent_ontology_filter'] = urllib.parse.unquote(self.kwargs['ontologyParent'])
                message += " -> {}".format(context['parent_ontology_filter'])
                parent = Ontology.objects.get(name=urllib.parse.unquote(self.kwargs['ontologyParent']))
                list_ontology_third_level = sorted(parent.get_children(), key=lambda x: unidecode(x.name.lower()))
                context['ontology_list_left_menu'] = OrderedDict()
                for x in list_ontology_third_level:
                    trans = x.name
                    with override('en'):
                        context['ontology_list_left_menu'][x.name] = trans
                #context['ontology_list_left_menu'] = parent.get_children().values_list('name', flat=True)
                context['root'] = False
                context['parent'] = True
                context['child'] = False
                if 'ontologyChild' in self.kwargs:
                    context['child_ontology_filter'] = urllib.parse.unquote(self.kwargs['ontologyChild'])
                    message += " -> {}".format(context['child_ontology_filter'])
                    #context['ontology_list_left_menu'] = parent.get_children().values_list('name', flat=True)
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
            message += " with difficulties: {}".format(context['difficulties_selected'])
        if 'course' in self.request.GET:
            context['course_selected'] = int(self.request.GET.get('course'))
            message += " for study program: {}".format(context['course_selected'])
        if 'language' in self.request.GET:
            context['languages_selected'] = [x for x in self.request.GET.getlist('language')]
            message += " with language: {}".format(context['languages_selected'])
        logger.info(message + "\n")
        cart = list(Cart(self.request)).__iter__()
        context['cart_view'] = cart
        context['exercises_ids'] = ','.join(list(self.request.session['cart'].keys()))
        return context

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .service import Cart
from django.utils.decorators import method_decorator
from collections import OrderedDict


class CartAPI(APIView):
    """
    Single API to handle cart operations
    """
    #renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]
    template_name = 'cart_list.html'

    def get(self, request, format=None):
        cart = Cart(request)
        if not cart.cart:
            return Response(
                status=status.HTTP_200_OK
                )
        else:
            exercises_ids = ','.join(list(self.request.session['cart'].keys()))
            return Response({"data": list(cart).__iter__(),
                             "exercises_ids": exercises_ids,
                             "exercises_number": cart.number_of_exercises()
                },
                            status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        cart = Cart(request)

        if "remove" in request.data:
            exercise = request.data["exercise"]
            cart.remove(exercise)
            exercises_ids = ','.join(list(self.request.session['cart'].keys()))
        elif "clear" in request.data:
            cart.clear()
            exercises_ids = ''
        else:
            product = request.data
            cart.add(
                    exercise=product["exercise"]
                )
            exercises_ids = ','.join(list(self.request.session['cart'].keys()))
        return Response(
            {"message": "cart updated",
             "exercises_ids": exercises_ids,
             "exercises_number": cart.number_of_exercises()},
            status=status.HTTP_202_ACCEPTED)

