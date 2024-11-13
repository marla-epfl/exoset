from django.shortcuts import render
from rest_framework import viewsets
from django.views.generic import ListView, DetailView, TemplateView
import requests
# Create your views here.
example_list = [
    {"id": 66,
            "filename": "e8a6358134cd459797036f716dc7e997.xml",
            "quiz_type": "SingleSelect",
            "fingerprint": "f43978935c0079c77e6c186c2ec43c4c",
            "quiz_title": "Question 1",
            "absolute_number_in_order": 3,
            "quiz_url": "null",
            "image_url": "null",
            "statement": "<p>What neurotransmitter do motor neurons release at the neuromuscular juction?</p>\n  ",
            "feedback": "<div class=\"detailed-solution\">\n      <p>Explanation</p>\n      <p>Motor neurons in vertebrates are cholinergic, which means that they release the neurotransmitter acetylcholine from synaptic vesicles at the neuromuscular junction.</p>\n    </div>\n  ",
            "img_1_path": "null",
            "img_1_width": "null",
            "img_1_height": "null",
            "img_1_alt": "null",
            "img_1_is_it_online_video": "null",
            "img_1_is_it_feedback": "null",
            "img_2_path": "null",
            "img_2_width": "null",
            "img_2_height": "null",
            "img_2_alt": "null",
            "img_2_is_it_online_video": "null",
            "img_2_is_it_feedback": "null",
            "img_3_path": "null",
            "img_3_width": "null",
            "img_3_height": "null",
            "img_3_alt": "null",
            "img_3_is_it_online_video": "null",
            "img_3_is_it_feedback": "null",
            "img_4_path": "null",
            "img_4_width": "null",
            "img_4_height": "null",
            "img_4_alt": "null",
            "img_4_is_it_online_video": "null",
            "img_4_is_it_feedback": "null",
            "options_text": [
                "Acetylcholine\n      ",
                "Glutamate\n      ",
                "Dopamine\n      ",
                "Glycine\n    "
            ],
            "options_is_it_correct": [
                "true",
                "false",
                "false",
                "false"
            ],
            "options_feedback": [
                "null",
                "null",
                "null",
                "null"
            ],
            "hints": "null",
            "compound_hint_ids": "null",
            "compound_hint_text": "null",
            "partial_credit": "null",
            "vertical": 1014,
            "course_title": "BIO_482",
            "quiz_concepts": ["concept1", "concept2", "concept3"],
            "ontology_trees": [],
            "language": "Français",
            "course_level": "master",
            "course_instructor": ["Teacher 1", "Teacher 2", "Teacher3"],
            "quiz_category": "Computer science"
        },
        {
            "id": 41,
            "filename": "18b8e4a34f14472f87b92841bc76aa62.xml",
            "quiz_type": "SingleSelect",
            "fingerprint": "494e0e6222dea79691fd5fb5b3c7975f",
            "quiz_title": "Question 1",
            "absolute_number_in_order": 2,
            "quiz_url": "null",
            "image_url": "null",
            "statement": "<p>What are the main excitatory and inhibitory neurotransmitters in the mammalian brain respectively?</p>\n  ",
            "feedback": "<div class=\"detailed-solution\">\n      <p>Explanation</p>\n      <p>The most important two neurotransmitters in the central nervous system are glutamate and gamma-aminobutyric acid (GABA). Glutamate is excitatory, driving the postsynaptic neuron towards ~0 mV membrane potential. GABA is inhibitory, driving the postsynaptic membrane potential towards ~-75 mV.</p>\n    </div>\n  ",
            "img_1_path": "null",
            "img_1_width": "null",
            "img_1_height": "null",
            "img_1_alt": "null",
            "img_1_is_it_online_video": "null",
            "img_1_is_it_feedback": "null",
            "img_2_path": "null",
            "img_2_width": "null",
            "img_2_height": "null",
            "img_2_alt": "null",
            "img_2_is_it_online_video": "null",
            "img_2_is_it_feedback": "null",
            "img_3_path": "null",
            "img_3_width": "null",
            "img_3_height": "null",
            "img_3_alt": "null",
            "img_3_is_it_online_video": "null",
            "img_3_is_it_feedback": "null",
            "img_4_path": "null",
            "img_4_width": "null",
            "img_4_height": "null",
            "img_4_alt": "null",
            "img_4_is_it_online_video": "null",
            "img_4_is_it_feedback": "null",
            "options_text": [
                "Arginine and GABAzine\n      ",
                "Dopamine and Glycine\n      ",
                "Glutamate and GABA\n      ",
                "Acetylcholine and Oxytocin\n    "
            ],
            "options_is_it_correct": [
                "false",
                "false",
                "true",
                "false"
            ],
            "options_feedback": [
                "null",
                "null",
                "null",
                "null"
            ],
            "hints": "null",
            "compound_hint_ids": "null",
            "compound_hint_text": "null",
            "partial_credit": "null",
            "vertical": 1003,
            "course_title": "BIO_482",
            "quiz_concepts": ["concept1", "concept2", "concept3"],
            "ontology_trees": [],
            "language": "Français",
            "course_level": "master",
            "course_instructor": ["Professor 1", "Assistant", "Teacher3"],
            "quiz_category": "Mathematics"
        }
]

example_filter = {
        "course_category": [{ "name" : "Mathematics", "id": 1}, { "name" : "Computer Science", "id": 2},
                            { "name" : "Chemistry", "id": 3}, { "name" : "Engineering", "id": 4},
                            { "name" : "Physics", "id": 5}, { "name" : "Architecture", "id": 6},
                            { "name" : "Mathematics_1", "id": 7}, { "name" : "Computer Science_1", "id": 8},
                            { "name" : "Chemistry_1", "id": 9}, { "name" : "Engineering_1", "id": 10},
                            { "name" : "Physics_1", "id": 11}, { "name" : "Architecture_1", "id": 12}],
        "course_level": [{ "name" : 'Master', "id": 1}, { "name" : "Bachelor", "id": 2}, { "name" : "Level 1", "id": 3},
                         { "name" : "Level 2", "id": 4}, { "name" : "Level 3", "id": 5}],
        "language": [{ "name" : "Français", "id": 1}, { "name" : "English", "id": 2}, { "name" : "Italiano", "id": 3}]
    }



class QuizzesListView(ListView):
    template_name = "list_quizzes.html"

    def get_queryset(self):
        filter_course_category = ''
        try:
            search_language = self.request.LANGUAGE_CODE
        except:
            search_language = 'en'
        filter_course_level = self.request.GET.getlist("course_level", '')
        if filter_course_level is not '':
            filter_course_level = ','.join(x for x in filter_course_level)
        filter_language = self.request.GET.getlist("language", '')
        if filter_language is not '':
            filter_language = ','.join(x for x in filter_language)
        if 'course_category' in self.kwargs and self.kwargs['course_category'] is not '':
            filter_course_category = self.kwargs['course_category']
        search = self.request.GET.get("search")
        if search is None:
            search = ''
        search_filter = '?language_code_page=' + search_language + '&language_codes=' + filter_language + '&limit=10&offset=0&search=' + str(search) + '&ontology_category_id='+ filter_course_category + '&study_levels=' + filter_course_level
        response = requests.get('https://cede-webapps.epfl.ch/open-quizzes-test/quizzes-exoset-search-and-filter/' + search_filter)
        data = response.json()
        #data = example_list
        return data['results']

    def get_filters(self):
        #  This is where the APIs are going to go.
        response = requests.get('https://cede-webapps.epfl.ch/open-quizzes-test/quizzes-exoset-all-filters/?language_code_page='+self.request.LANGUAGE_CODE)
        data = response.json()
        #data = example_filter
        return data

    def get_context_data(self, **kwargs):
        context = super(QuizzesListView, self).get_context_data(**kwargs)
        filters = self.get_filters()
        context['course_categories'] = filters['ontology_categories']
        context['course_level'] = filters['study_levels']
        context['languages_list'] = filters['language_codes']
        if "course_category" in self.kwargs:
            if self.kwargs['course_category'] is not '':
                context['course_category_selected'] = int(self.kwargs["course_category"])
        if "course_level" in self.request.GET:
            context['course_level_selected'] = [x for x in self.request.GET.getlist('course_level')]
        if "language" in self.request.GET:
            context['language_selected'] = [x for x in self.request.GET.getlist('language')]
        return context


class QuizzesDetailView(TemplateView):
    template_name = 'quiz_detail.html'

    def get_context_data(self, **kwargs):
        context = super(QuizzesDetailView, self).get_context_data(**kwargs)
        response = requests.get('https://cede-webapps.epfl.ch/open-quizzes-test/quizzes-exoset-detail/?language_code_page=' + self.request.LANGUAGE_CODE + '&quiz_id=' + self.kwargs['quiz_id'])
        context['object'] = response.json()
        context['category'] = context['object']['ontology_trees'][0]['ontology_category_depth_2']['name']
        context['ontology_tree_1'] = (((context['object']['ontology_trees'][0]['ontology_category_depth_1']['name']
                                      + ' > ' +
                                      context['object']['ontology_trees'][0]['ontology_category_depth_2']['name'])
                                      + ' > ' +
                                      context['object']['ontology_trees'][0]['ontology_category_depth_3']['name'])
                                      + ' > ' +
                                      context['object']['ontology_trees'][0]['ontology_category_depth_4']['name'])
        try:
            context['ontology_tree_2'] = (context['object']['ontology_trees'][1]['ontology_category_depth_1']['name'] +
                                           ' > ' +
                                           context['object']['ontology_trees'][1]['ontology_category_depth_2']['name'] +
                                           ' > ' +
                                           context['object']['ontology_trees'][1]['ontology_category_depth_3']['name'] +
                                           ' > ' +
                                           context['object']['ontology_trees'][1]['ontology_category_depth_4']['name'])
        except IndexError:
            context['ontology_tree_2'] = ''

        return context

