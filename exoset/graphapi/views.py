from django.shortcuts import render

# Create your views here.
from exoset.tag.models import TagConcept
from exoset.ontology.models import DocumentCategory, WikiConceptOntology, Ontology
from exoset.document.models import Resource


def search_concept_in_ontology(concept):
    list_pk_resources = []
    try:
        list_ontologies_for_concept = WikiConceptOntology.objects.get(concept=concept).list_ontologies()
        for ontology in list_ontologies_for_concept:
            list_pk_resources.extend(Ontology.objects.get(id=ontology).get_resources())
    except WikiConceptOntology.DoesNotExist:
        return list_pk_resources
    return list_pk_resources

def search_by_concept(concept, language=None):
    """
    create json from concept
    """
    if concept[-1] == ',':
        concept = concept[:-1]
    if language:
        list_concept_objects = TagConcept.objects.filter(label__iexact=concept, resource__language=language)
    else:
        list_concept_objects = TagConcept.objects.filter(label__iexact=concept)
    list_exercises_with_concept = [x.resource_id for x in list_concept_objects]
    list_document_categories = DocumentCategory.objects.filter(resource_id__in=list_exercises_with_concept)
    list_ontologies_from_document_categories = [x.category_id for x in list_document_categories if x.resource.visible]
    unique_ontologies = list(set(list_ontologies_from_document_categories))
    list_exercises_with_concept_in_ontology = search_concept_in_ontology(concept)
    ontology_dict = {}
    website = 'https://test-exoset.epfl.ch/resources/'
    #list_exercises = [x.resource_id for x in
    #                  DocumentCategory.objects.filter(category_id__in=list_ontologies_from_document_categories)]
    dict_exercises = []
    list_exercises = []
    for ontology in unique_ontologies:
        if language:
            list_exercises_of_ontology = [x.resource_id for x in DocumentCategory.objects.filter(category_id=ontology,
                                                                                                 resource__visible=True,
                                                                                                 resource__language=language)]
        else:
            list_exercises_of_ontology = [x.resource_id for x in DocumentCategory.objects.filter(category_id=ontology,
                                                                                                 resource__visible=True)]
        list_exercises_of_ontology_with_concept = \
            list(set(list_exercises_of_ontology).intersection(list_exercises_with_concept))
        total_exercises_for_ontology = len(list_exercises_of_ontology)
        ontology_score = len(list_exercises_of_ontology_with_concept)/total_exercises_for_ontology
        ontology_dict[ontology] = (list_exercises_of_ontology, list_exercises_of_ontology_with_concept, ontology_score)
        for x in list_exercises_of_ontology:
            try:
                resource = Resource.objects.get(id=x)
                file_path = resource.filepath_info
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
                    dict_exercises[existing_exercise_index]['total_score'] = exercise_score
                    #print("changed score for exercise ", x)
            else:
                list_exercises.append(x)
                dict_exercises.append(
                    {'title': resource.title,
                     'url': website + resource.slug,
                     'score': exercise_score,
                     'ontology_score': 0,
                     'language': resource.language,
                     'level': resource.tag_level,
                     'author': file_path[0],
                     'langue_file': file_path[1],
                     'series': file_path[2],
                     'exercise': file_path[3],
                     'total_score': exercise_score
                     })
    for resource_pk in list_exercises_with_concept_in_ontology:
        try:
            resource_ = Resource.objects.get(pk=resource_pk)
            if not resource_.visible:
                pass
            file_path = resource_.filepath_info
            if resource_pk in list_exercises:
                existing_exercise_index = list_exercises.index(resource_pk)
                dict_exercises[existing_exercise_index]['ontology_score'] = 2
                dict_exercises[existing_exercise_index]['total_score'] = (
                    dict_exercises[existing_exercise_index]['score'] + 2)
            else:
                list_exercises.append(resource_pk)
                dict_exercises.append(
                    {'title': resource_.title,
                     'url': website + resource_.slug,
                     'score': 0,
                     'ontology_score': 2,
                     'language': resource_.language,
                     'level': resource.tag_level,
                     'author': file_path[0],
                     'langue_file': file_path[1],
                     'series': file_path[2],
                     'exercise': file_path[3],
                     'total_score': 2
                     })
        except Resource.DoesNotExist:
            pass
            #dict_exercises.append({'title': resource.title, 'url': website + resource.slug, 'score': exercise_score})
        # result[ontology] = {e: s for e, s in zip(list_exercises_of_ontology, list_score_concept)}
    return dict_exercises


from rest_framework.views import APIView
from rest_framework.response import Response


class ListExercises(APIView):

    def post(self, request):
        concept = self.request.POST["concept"]
        language = None
        if 'language' in self.request.POST.keys():
            language = self.request.POST["language"]
            if language.upper() in 'FRANÇAIS':
                language = 'FR'
            else:
                language = 'EN'
        #else:
        #    language = 'ENGLISH'
        if concept:
            list_exercises = search_by_concept(concept, language)
        return Response(list_exercises)

    def get(self, request):
        concept = request.query_params["concept"]
        language = None
        if 'language' in request.query_params.keys():
            language = request.query_params["language"]
            if language.upper() in 'FRANÇAIS':
                language = 'FR'
            else:
                language = 'EN'
        #else:
        #    language = 'ENGLISH'
        if concept:
            list_exercises = search_by_concept(concept, language)
        return Response(list_exercises)


