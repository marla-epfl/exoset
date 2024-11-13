
from django.urls import include, path
from .views import QuizzesListView, QuizzesDetailView
app_name = "quiz"

urlpatterns = [
    path("quiz_<str:quiz_id>", QuizzesDetailView.as_view(), name='quiz_detail'),
    path("<str:course_category>", QuizzesListView.as_view(), name='quizzes_list_category_filter'),
    path("", QuizzesListView.as_view(), name='quizzes_list'),

    #path("<slug:slug>", NotebookDetailView.as_view(), name='notebook_detail'),
]
