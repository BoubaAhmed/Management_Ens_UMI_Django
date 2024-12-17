from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.etudiant_login, name='etudiant_login'),
    path('dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('logout/', views.etudiant_logout, name='etudiant_logout'),
]
