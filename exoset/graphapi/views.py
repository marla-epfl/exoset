from django.shortcuts import render

# Create your views here.
from exoset.tag.models import TagConcept
from exoset.ontology.models import DocumentCategory
from exoset.document.models import Resource


def search_by_concept(concept, language='ENGLISH'):
    """
    create json from concept
    """
    print(language)
    if concept[-1] == ',':
        concept = concept[:-1]
    list_concept_objects = TagConcept.objects.filter(label__iexact=concept, resource__language=language)
    list_exercises_with_concept = [x.resource_id for x in list_concept_objects]
    list_document_categories = DocumentCategory.objects.filter(resource_id__in=list_exercises_with_concept)
    list_ontologies_from_document_categories = [x.category_id for x in list_document_categories if x.resource.visible]
    unique_ontologies = list(set(list_ontologies_from_document_categories))
    ontology_dict = {}
    website = 'https://exoset.epfl.ch/resources/'
    #list_exercises = [x.resource_id for x in
    #                  DocumentCategory.objects.filter(category_id__in=list_ontologies_from_document_categories)]
    dict_exercises = []
    list_exercises = []
    for ontology in unique_ontologies:
        list_exercises_of_ontology = [x.resource_id for x in DocumentCategory.objects.filter(category_id=ontology,
                                                                                             resource__visible=True,
                                                                                             resource__language=language)]
        list_exercises_of_ontology_with_concept = \
            list(set(list_exercises_of_ontology).intersection(list_exercises_with_concept))
        total_exercises_for_ontology = len(list_exercises_of_ontology)
        ontology_score = len(list_exercises_of_ontology_with_concept)/total_exercises_for_ontology
        ontology_dict[ontology] = (list_exercises_of_ontology, list_exercises_of_ontology_with_concept, ontology_score)
        for x in list_exercises_of_ontology:
            try:
                resource = Resource.objects.get(id=x)
            except Resource.DoesNotExist:
                pass
            if not resource.visible:
                pass
            ontology_score = round(ontology_score, 5)
            if x in list_exercises_with_concept:
                exercise_score = 1 + ontology_score
                #list_score_concept.append(exercise_score)
            else:
                exercise_score = ontology_score
                #list_score_concept.append(exercise_score)
            if x in list_exercises:
                # check if the exercise is already in the dictionary
                existing_exercise_index = list_exercises.index(x)
                if dict_exercises[existing_exercise_index]['score'] > exercise_score:
                    # check if the score of the exercise is higher of the existing one, if so go to the next exercise,
                    # if not replace the existing score with the new one
                    #print("remain score for exercise ", x)
                    pass
                else:
                    dict_exercises[existing_exercise_index]['score'] = exercise_score
                    #print("changed score for exercise ", x)
            else:
                list_exercises.append(x)
                dict_exercises.append(
                    {'title': resource.title,
                     'url': website + resource.slug,
                     'score': exercise_score,
                     'language': resource.language
                     })
            #dict_exercises.append({'title': resource.title, 'url': website + resource.slug, 'score': exercise_score})
        # result[ontology] = {e: s for e, s in zip(list_exercises_of_ontology, list_score_concept)}
    return dict_exercises


from rest_framework.views import APIView
from rest_framework.response import Response


class ListExercises(APIView):

    def post(self, request):
        concept = self.request.POST["concept"]
        print(concept)
        if 'language' in self.request.POST.keys():
            language = self.request.POST["language"]
            print("language",language)
            if language.upper() in 'FRANÇAIS':
                language = 'FRANÇAIS'
            else:
                language = 'ENGLISH'
        else:
            language = 'ENGLISH'
        if concept:
            list_exercises = search_by_concept(concept, language)
        return Response(list_exercises)

    def get(self, request):
        concept = request.query_params["concept"]
        if 'language' in request.query_params.keys():
            language = request.query_params["language"]
            if language.upper() in 'FRANÇAIS':
                language = 'FRANÇAIS'
            else:
                language = 'ENGLISH'
        else:
            language = 'ENGLISH'
        if concept:
            list_exercises = search_by_concept(concept, language)
        return Response(list_exercises)


