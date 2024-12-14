from django.urls import path
from . import views, chatbot


urlpatterns = [
    # ---------------------- Utilisateur URLs ----------------------
    path('utilisateur/', views.utilisateur_list, name='utilisateur_list'),
    path('utilisateur/<int:pk>/', views.utilisateur_detail, name='utilisateur_detail'),
    path('utilisateur/create/', views.create_utilisateur, name='create_utilisateur'),
    path('utilisateur/edit/<int:pk>/', views.update_utilisateur, name='edit_utilisateur'),
    path('utilisateur/delete/<int:pk>/', views.delete_utilisateur, name='delete_utilisateur'),
    path('export_utilisateurs/', views.export_utilisateurs_excel, name='export_utilisateurs'),
    
    # ---------------------- Filiere URLs ----------------------
    path('filiere/', views.filiere_list, name='filiere_list'),
    path('filiere/<int:pk>/', views.filiere_detail, name='filiere_detail'),
    path('filiere/create/', views.create_filiere, name='create_filiere'),
    path('filiere/edit/<int:pk>/', views.update_filiere, name='edit_filiere'),
    path('filiere/delete/<int:pk>/', views.delete_filiere, name='delete_filiere'),

    # ---------------------- Module URLs ----------------------
    path('module/', views.module_list, name='module_list'),
    path('module/<int:pk>/', views.module_detail, name='module_detail'),
    path('module/create/', views.create_module, name='create_module'),
    path('module/edit/<int:pk>/', views.update_module, name='edit_module'),
    path('module/delete/<int:pk>/', views.delete_module, name='delete_module'),

    # ---------------------- Groupe URLs ----------------------
    path('groupe/', views.groupe_list, name='groupe_list'),
    path('groupe/<int:pk>/', views.groupe_detail, name='groupe_detail'),
    path('groupe/create/', views.create_groupe, name='create_groupe'),
    path('groupe/edit/<int:pk>/', views.update_groupe, name='edit_groupe'),
    path('groupe/delete/<int:pk>/', views.delete_groupe, name='delete_groupe'),

    # ---------------------- Etudiant URLs ----------------------
    path('etudiant/', views.etudiant_list, name='etudiant_list'),
    path('etudiant/<int:pk>/', views.etudiant_detail, name='etudiant_detail'),
    path('etudiant/create/', views.create_etudiant, name='create_etudiant'),
    path('etudiant/edit/<int:pk>/', views.update_etudiant, name='edit_etudiant'),
    path('etudiant/delete/<int:pk>/', views.delete_etudiant, name='delete_etudiant'),

    # ---------------------- Note URLs ----------------------
    path('note/', views.note_list, name='note_list'),
    path('note/<int:pk>/', views.note_detail, name='note_detail'),
    path('note/create/', views.create_note, name='create_note'),
    path('note/edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('note/delete/<int:pk>/', views.delete_note, name='delete_note'),

    path('get-groupes/', views.get_groupes, name='get_groupes'),
    path('get-etudiants/', views.get_etudiants, name='get_etudiants'),
    path('get-modules/', views.get_modules, name='get_modules'),
    

    path('chatbot/', chatbot.chatbot_response , name='chatbot_response'),
    path('assistant/', views.assistant, name='chatbot_assistant'),
]
