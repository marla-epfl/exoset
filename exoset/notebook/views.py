from django.shortcuts import render
from exoset.notebook.models import GitRepository, Notebook, Kernel, NBType
from django.views.generic import DetailView, ListView, TemplateView
# Create your views here.

FR = "FRANÇAIS"
IT = "ITALIANO"
EN = "ENGLISH"

LANGUAGES_CHOICES = (
        (FR, "Français"),
        (EN, "English"),
    )


class GitRepositoryList(ListView):
    model = GitRepository
    template_name = 'gitrepository_list.html'
    paginate_by = 10


class NotebookList(ListView):
    model = Notebook
    template_name = 'notebooks_list.html'
    paginate_by = 10

    def get_queryset(self):
        list_notebooks = Notebook.objects.all()
        if "language" in self.request.GET:
            languages = self.request.GET.getlist("language")
            list_notebooks = list_notebooks.filter(language__in=languages)
        if "kernel" in self.request.GET:
            kernels = self.request.GET.getlist("kernel")
            list_notebooks = list_notebooks.filter(git_repository__kernel__kernel__in=kernels)
        if "type" in self.request.GET:
            types = self.request.GET.getlist("type")
            list_notebooks = list_notebooks.filter(nb_type__in=types)
        return list_notebooks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types_list'] = NBType.objects.all()
        context['languages_list'] = LANGUAGES_CHOICES
        context['kernels_list'] = Kernel.objects.all()
        if 'type' in self.request.GET:
            context['types_selected'] = [int(x) for x in self.request.GET.getlist('type')]
            #message += " with difficulties: {}".format(context['difficulties_selected'])
        if 'kernel' in self.request.GET:
            try:
                context['kernels_selected'] = [int(x) for x in self.request.GET.getlist('kernel')]
                #message += " for study program: {}".format(context['course_selected'])
            except ValueError:
                pass
        if 'language' in self.request.GET:
            context['languages_selected'] = [x for x in self.request.GET.getlist('language')]
            #message += " with language: {}".format(context['languages_selected'])
        return context


class NotebookDetailView(DetailView):
    model = Notebook
    template_name = 'notebooks_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NotebookDetailView, self).get_context_data(**kwargs)
        notebook = Notebook.objects.get(slug=self.kwargs['slug'])
        context['html_view'] = notebook.html_view
        list_notebooks_path = notebook.get_notebook_rel_path()
        context['files'] = list_notebooks_path
        return context


class FileExplorerTemplateView(TemplateView):
    template_name = 'file_explorer.html'
    def get_context_data(self, **kwargs):
        context = super(FileExplorerTemplateView, self).get_context_data(**kwargs)
        notebook = Notebook.objects.get(slug=self.kwargs['slug'])
        list_notebooks_path = GitRepository.objects.get(notebook=notebook).get_ipynb_rel_path()
        context['files'] = [
            {'name': 'folder1',
             'children': [
                 {'name': 'folder1_1',
                  'children': [
                      {'name': 'folder1_1_1',
                       'children': [{'name': 'NB1',
                                     'children': []
                                     }
                                    ]
                       },
                      {'name': 'folder1_1_2',
                       'children': [{'name': 'NB2',
                                     'children': []
                                     }
                                    ]
                       },
                  ]
                  }
             ]
             },
            {'name': 'folder2',
             'children': [
                 {'name': 'NB3',
                  'children': []
                  }
             ]
             },
            {'name': 'folder3',
             'children': [
                 {'name': 'folder3_1',
                  'children': [
                      {'name': 'NB4',
                       'children': []
                       }
                  ]
                  }
             ]
             }
        ]

        return context

