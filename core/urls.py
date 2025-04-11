from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from . import views
from .views.question import QuestionSearchView


urlpatterns = [
    path('', views.QuestionListView.as_view(), name='question_list'),
    path('question/<int:pk>/', login_required(views.QuestionDetailView.as_view()), name='question_detail'),
    path('ask/', login_required(views.QuestionCreateView.as_view()), name='ask_question'),
    path('answer/<int:answer_id>/like/', login_required(views.like_answer), name='like_answer'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('search/', login_required(QuestionSearchView.as_view()), name='question_search'),
    path('api/search/', login_required(QuestionSearchView.as_view()), name='api_question_search'),
]

# Custom login view to handle already logged-in users
def custom_login(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('question_list')
    return LoginView.as_view()(request, *args, **kwargs)

# Custom logout view to handle both GET and POST
def custom_logout(request):
    if request.method == 'GET':
        return redirect('question_list')
    return LogoutView.as_view(next_page='question_list')(request)

# Add login and logout URLs
urlpatterns += [
    path('accounts/login/', custom_login, name='login'),
    path('accounts/logout/', custom_logout, name='logout'),
] 