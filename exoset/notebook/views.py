from django.shortcuts import render
from exoset.notebook.models import GitRepository, Notebook
from django.views.generic import DetailView, ListView, TemplateView
# Create your views here.


class GitRepositoryList(ListView):
    model = GitRepository
    template_name = 'gitrepository_list.html'
    paginate_by = 10


class NotebookList(ListView):
    model = Notebook
    template_name = 'notebooks_list.html'
    paginate_by = 10


class NotebookDetailView(DetailView):
    model = Notebook
    template_name = 'notebooks_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NotebookDetailView, self).get_context_data(**kwargs)
        notebook = Notebook.objects.get(slug=self.kwargs['slug'])
        context['html_view'] = notebook.html_view
        list_notebooks_path = GitRepository.objects.get(notebook=notebook).get_ipynb_rel_path()
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

