import django
django.setup()
from exoset.document.models import Resource, ResourceSourceFile, Document, update_filename
from exoset.ontology.models import DocumentCategory, Ontology
from exoset.tag.models import TagConcept, TagLevel, TagLevelResource, QuestionTypeResource, QuestionType
from exoset.prerequisite.models import Prerequisite, AssignPrerequisiteResource
from exoset.accademic.models import Course
from django.core.files.base import File
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exoset.config.settings")
title_string = '%title='
language_string = '%language='
difficulty_string = '%difficulty_level='
question_type_string = '%question_type='
ontology1_string = '%ontology1='
ontology2_string = '%ontology2='
concept1_string = '%concept1='
concept2_string = '%concept2='
concept3_string = '%concept3='
concept4_string = '%concept4='
concept5_string = '%concept5='
prerequisite1_string = '%prerequisite1='
prerequisite2_string = '%prerequisite2='
prerequisite3_string = '%prerequisite3='
prerequisite4_string = '%prerequisite4='
prerequisite5_string = '%prerequisite5='
def generate_variables(filename, exercise_name):
    ontology2 = concept1 = concept2 = concept3 = concept4 = concept5 = prerequisite1 = prerequisite2 = prerequisite3 = prerequisite4 = prerequisite5 = ''
    metadata = {}
    with open(filename, 'r') as f:
        for line in f:
            if title_string in line:
                metadata['title'] = line.split('=')[1]
            elif language_string in line:
                if 'fra' in language_string:
                    metadata['language'] = 'FR'
                else:
                    metadata['language'] = 'EN'
            elif question_type_string in line:
                metadata['question_type'] = line.split('=')[1]
            elif difficulty_string in line:
                metadata['difficulty'] = line.split('=')[1]
            elif ontology1_string in line:
                metadata['ontology1'] = line.split('=')[1]
            elif ontology2_string in line:
                if not '=(optional)' in line:
                    metadata['ontology2'] = line.split('=')[1]
            elif concept1_string in line:
                if not '%concept1=(optional)' in line:
                    metadata['concept1'] = line.split('=')[1]
            elif concept2_string in line:
                if not '%concept2=(optional)' in line:
                    metadata['concept2'] = line.split('=')[1]
            elif concept3_string in line:
                if not '%concept3=(optional)' in line:
                    metadata['concept3'] = line.split('=')[1]
            elif concept4_string in line:
                if not '%concept4=(optional)' in line:
                    metadata['concept4'] = line.split('=')[1]
            elif concept5_string in line:
                if not '%concept5=(optional)' in line:
                    metadata['concept5'] = line.split('=')[1]
            elif prerequisite1_string in line:
                if not '%prerequisite1=choose from graphsearch' in line:
                    metadata['prerequisite1'] = line.split('=')[1]
            elif prerequisite2_string in line:
                if not '%prerequisite2=choose from graphsearch' in line:
                    metadata['prerequisite2'] = line.split('=')[1]
            elif prerequisite3_string in line:
                if not '%prerequisite3=choose from graphsearch' in line:
                    metadata['prerequisite3'] = line.split('=')[1]
            elif prerequisite4_string in line:
                if not '%prerequisite4=choose from graphsearch' in line:
                    metadata['prerequisite4'] = line.split('=')[1]
            #elif prerequisite5_string in line:
            #    if not '%prerequisite5=choose  from concept (english only).' in line:
            #        metadata['prerequisite5'] = line.split('=')[1]
            #        print('5')
    create_resource(metadata, exercise_name)


def question_type_object(question_type):
    question_type_obj, created = QuestionType.objects.get_or_create(label=question_type)
    if created:
        print("Question type {} created, with pk {}".format(question_type, str(question_type_obj.pk)))
    else:
        print("Question type {} already exists and the pk is {}".format(question_type, str(question_type_obj.pk)))
    return question_type_obj.pk


def create_question_type_tag(question_type, resource_pk):
    question_type_pk = question_type_object(question_type)
    try:
        question_type_resource = QuestionTypeResource.objects.get(question_type_id=question_type_pk,
                                                                  resource_id=resource_pk)
        print("question_type_resource {} already exists".format(question_type_resource.pk))
    except QuestionTypeResource.DoesNotExist:
        question_type_resource = QuestionTypeResource.objects.create(question_type_id=question_type_pk,
                                                                     resource_id=resource_pk)
        print("question_type_resource {} has been created".format(question_type_resource.pk))


def level_object(difficulty):
    print("Level {}".format(difficulty))
    try:
        level_obj = TagLevel.objects.get(label__icontains=difficulty.strip())
    except TagLevel.DoesNotExist:
        print("ERROR ----- tag level not found {}".format(difficulty))
        level_obj = TagLevel.objects.get(label__icontains='Standard')
    return level_obj.pk


def create_level_tag(difficulty, resource_pk):
    tag_level_pk = level_object(difficulty)
    try:
        tag_level_resource = TagLevelResource.objects.get(resource_id=resource_pk)
        tag_level_resource.tag_level_id = tag_level_pk
        tag_level_resource.save()
        print("tag_level_resource {} already exists".format(tag_level_resource.pk))
    except TagLevelResource.DoesNotExist:
        tag_level_resource = TagLevelResource.objects.create(tag_level_id=tag_level_pk,
                                                                     resource_id=resource_pk)
        print("tag_level_resource {} has been created".format(tag_level_resource.pk))


def create_concept_tag(concept, resource_pk):

    try:
        tag_concept_resource = TagConcept.objects.get(label=concept, resource_id=resource_pk)
        print("tag_concept_resource {} with the concept {} exists already".format(tag_concept_resource.pk, concept))
    except TagConcept.DoesNotExist:
        tag_concept_resource = TagConcept.objects.create(label=concept, resource_id=resource_pk)
        print("tag_concept_resource {} has been created with the concept {}".format(tag_concept_resource.pk, concept))


def create_prerequisite_tag(prerequisite, resource_pk):
    prerequisite_obj, created = Prerequisite.objects.get_or_create(label=prerequisite)
    try:
        prerequisite_resource = AssignPrerequisiteResource.objects.get(resource_id=resource_pk)
        prerequisite_resource.prerequisite.add(prerequisite_obj)
        print("prerequisite {} has been added to the resource {}".format(prerequisite, resource_pk))
    except AssignPrerequisiteResource.DoesNotExist:
        prerequisite_resource = AssignPrerequisiteResource.objects.create(resource_id=resource_pk)
        prerequisite_resource.prerequisite.add(prerequisite_obj)
        print("tag_prerequisite_resource {} has been created with the prerequisite {}".format(prerequisite_resource.pk, prerequisite))


def ontology_object(ontology):
    print("ontology object {}".format(ontology))
    try:
        ontology = Ontology.objects.get(name__iexact=ontology.strip())
    except Ontology.DoesNotExist:
        ontology = Ontology.objects.filter(name__icontains=ontology.strip())[0]
        print("Ontology {} does not exist, first one has been chosen".format(ontology))
        ontology = None
    return ontology.pk

def create_ontology_tag(ontology1, ontology2, resource_pk):
    print("inside funtion {} and 2 is {}".format(ontology1, ontology2))
    tag_ontology_id = ontology_object(ontology1)
    try:
        DocumentCategory.objects.get(category_id=tag_ontology_id, resource_id=resource_pk)
    except DocumentCategory.DoesNotExist:
        DocumentCategory.objects.create(category_id=tag_ontology_id, resource_id=resource_pk)
    if len(ontology2) > 0:
        print("not right")
        tag_ontology_id2 = ontology_object(ontology2)
        try:
            DocumentCategory.objects.get(category_id=tag_ontology_id2, resource_id=resource_pk)
        except DocumentCategory.DoesNotExist:
            DocumentCategory.objects.create(category_id=tag_ontology_id2, resource_id=resource_pk)


def compile_pdf(exercise_name, resource_pk):
    github_path = '/app/exoset/media/github/math/'
    enonce_pdf = github_path + exercise_name + "/Compile_" + exercise_name + "_ENONCE.pdf"
    solution_pdf = github_path + exercise_name + "/Compile_" + exercise_name + "_ENONCE_SOLUTION.pdf"
    new_statement = Document()
    # compile in any case the latex (compiles twice for references to work in latex)
    os.system("cd " + github_path + exercise_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
              exercise_name + "_ENONCE.tex")
    os.system("cd " + github_path + exercise_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
              exercise_name + "_ENONCE.tex ; rm *.aux *.log *.aux *.dvi;")
    os.system("cd " + github_path + exercise_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
              exercise_name + "_ENONCE_SOLUTION.tex")
    os.system("cd " + github_path + exercise_name + " ; pdflatex -interaction=nonstopmode -halt-on-error Compile_" +
              exercise_name + "_ENONCE_SOLUTION.tex ; rm *.aux *.log *.aux *.dvi;")
    with open(enonce_pdf, 'rb') as f:
        new_name = update_filename(new_statement, enonce_pdf.split(github_path + exercise_name)[1])
        new_statement.resource_id = resource_pk
        new_statement.document_type = 'STATEMENT'
        new_statement.file.save(new_name, File(f))
    new_solution = Document()
    with open(solution_pdf, 'rb') as f:
        new_name_sol = update_filename(new_solution, solution_pdf.split(github_path + exercise_name)[1])
        new_solution.resource_id = resource_pk
        new_solution.document_type = 'SOLUTION'
        new_solution.file.save(new_name_sol, File(f))
        print(new_statement.pk)

def create_resource(metadata, exercise_name):
    print("starting creation of resource")
    resource, created = Resource.objects.get_or_create(title=metadata['title'],
                                                      language=metadata['language'],
                                                      creator_id=1,
                                                      author='Analyses I')
    if not created:
        print("resource {} already exists".format(resource.pk))
        path = ResourceSourceFile.objects.get(resource_id=resource.pk).source
        #print(path)
        print("exercise name")
        #print(exercise_name)
        if not exercise_name in path:
            resource = Resource.objects.create(title=metadata['title'] + ' ',
                                                           language=metadata['language'],
                                                           creator_id=1,
                                                           author='Analyses I')
    else:
        print("resource {} has been created".format(resource.pk))
    try:
        print("find resource source file")
        print(resource.pk)
        resource_source_file = ResourceSourceFile.objects.get(resource_id=resource.pk,
                                                              source="/app/exoset/media/github/math/" + exercise_name,
                                                              style='/app/exoset/media/github/math/cartouche/Analysis')
        print("resource_source_file {} exists".format(resource_source_file.pk))
    except ResourceSourceFile.DoesNotExist:
        resource_source_file = ResourceSourceFile.objects.create(resource=resource,
                                                                 source="/app/exoset/media/github/math/" + exercise_name,
                                                                 style='/app/exoset/media/github/math/cartouche/Analysis')
        print("resource_source_file {} created".format(resource_source_file.pk))

    # create question type tag
    create_question_type_tag(metadata['question_type'], resource.pk)
    #create tag_level tag
    create_level_tag(metadata['difficulty'], resource.pk)
    # create concept tag

    if 'concept1' in metadata.keys():
        create_concept_tag(metadata['concept1'], resource.pk)
        print("creating tag concept {} ".format(metadata['concept1']))
    if 'concept2' in metadata.keys():
        create_concept_tag(metadata['concept2'], resource.pk)
        print("creating tag concept {} ".format(metadata['concept2']))
    if 'concept3' in metadata.keys():
        create_concept_tag(metadata['concept3'], resource.pk)
        print("creating tag concept {} ".format(metadata['concept3']))
    if 'concept4' in metadata.keys():
        create_concept_tag(metadata['concept4'], resource.pk)
        print("creating tag concept {} ".format(metadata['concept4']))
    if 'concept5' in metadata.keys():
        create_concept_tag(metadata['concept5'], resource.pk)
        print("creating tag concept {} ".format(metadata['concept5']))
    #create prerequisite tag
    if 'prerequisite1' in metadata.keys():
        create_prerequisite_tag(metadata['prerequisite1'], resource.pk)
        print("creating tag prerequisite {} ".format(metadata['prerequisite1']))
    if 'prerequisite2' in metadata.keys():
        create_prerequisite_tag(metadata['prerequisite2'], resource.pk)
        print("creating tag prerequisite {} ".format(metadata['prerequisite2']))
    if 'prerequisite3' in metadata.keys():
        create_prerequisite_tag(metadata['prerequisite3'], resource.pk)
        print("creating tag prerequisite {} ".format(metadata['prerequisite3']))
    if 'prerequisite4' in metadata.keys():
        create_prerequisite_tag(metadata['prerequisite4'], resource.pk)
        print("creating tag prerequisite {} ".format(metadata['prerequisite4']))
    #if 'prerequisite5' in metadata.keys():
    #    create_prerequisite_tag(metadata['prerequisite5'], resource.pk)
    #    print("creating tag prerequisite {} ".format(metadata['prerequisite5']))


    # create ontology tag
    if 'ontology2' in metadata.keys():
        print("metadata 1 is {} and ontology 2 is {}".format(metadata['ontology1'], metadata['ontology2']))
        create_ontology_tag(metadata['ontology1'], metadata['ontology2'], resource.pk)

    else:
        print("ontology 1 is {}".format(metadata['ontology1']))
        create_ontology_tag(metadata['ontology1'], "", resource.pk)
    compile_pdf(exercise_name, resource.pk)
    print(str(resource.pk), str(resource_source_file.pk))

def main():
    for root, dirs, files in os.walk('/home/maria/Downloads/math'):
        for file in files:
            if file.endswith('ENONCE_SOLUTION.tex'):
                exercise_name = os.path.join(root, file)
                path_dir = os.path.dirname(exercise_name)
                #print(os.path.split(path_dir)[-1])
                generate_variables(exercise_name, os.path.split(path_dir)[-1])

        #for file in files:
        #    if file.endswith('ENONCE_SOLUTION.tex'):
        #        print(file)
    #generate_variables('/home/maria/Downloads/math/Analysis_FR_S01_E01/Compile_Analysis_FR_S01_E01_ENONCE_SOLUTION.tex', 'Analysis_FR_S01_E01')


if __name__ == '__main__':
    main()
