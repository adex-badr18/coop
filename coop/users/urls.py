from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('ajax/load-lg/', views.load_lg, name='ajax_load_lg'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('update_password/', views.update_password, name='update_password'),
    path('update_profile/', views.user_profile_update, name='profile_update'),
]
