from django.urls import path, include
from . import views
from .views import CustomLoginView

urlpatterns = [
    # -----------------------
    # Page Views
    # -----------------------
    path('', views.home, name='home'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('student/', views.student_page, name='student_page'),
    path('educator/', views.educator_page, name='educator_page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('educator/dashboard/', views.educator_dashboard, name='educator_dashboard'),
    path('student/logout/', views.student_logout, name='student_logout'),
    path('educator/logout/', views.educator_logout, name='educator_logout'),

    # -----------------------
    # Authentication Views
    # -----------------------
    path('student/login/', views.student_login, name='student_login'),
    path('student/signup/', views.student_signup, name='student_signup'),
    path('educator/login/', views.educator_login, name='educator_login'),
    path('educator/signup/', views.educator_signup, name='educator_signup'),

    # -----------------------
    # Password Reset URLs
    # -----------------------
    path('password_reset/', include('django.contrib.auth.urls')),

    # -----------------------
    # API Endpoints
    # -----------------------
    path('api/login/', views.user_login, name='api_login'),
    path('api/get_badge/', views.get_badge, name='get_badge'),
    path('api/update_leaderboard/', views.update_leaderboard, name='update_leaderboard'),
    path('api/get_quiz/', views.get_quiz, name='get_quiz'),
    path('api/submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('api/assign_quiz/', views.assign_quiz, name='assign_quiz'),
    path('api/get_progress/', views.get_progress, name='get_progress'),
]
