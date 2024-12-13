from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Utilisateur, Filiere, Module, Groupe, Etudiant, Note
from .forms import (
    UtilisateurForm, FiliereForm, ModuleForm, GroupeForm, EtudiantForm, NoteForm
)
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from django.http import HttpResponse
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Utilisateur
from django.http import JsonResponse

def is_staff_and_active(view_func):
    """
    Decorator to ensure the user is both staff and active.
    Redirects with an error message if not.
    """
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated: 
            if not request.user.is_staff or not request.user.is_active:
                messages.error(request, "You do not have the required permissions.")
                return redirect('login')  # Redirect to the login page or an error page
        else:
            messages.error(request, "You must log in first.")
            return redirect('login') # Redirect to the login page

        return view_func(request, *args, **kwargs)

    return wrapper


# ---------------------- Views Utilisateur ----------------------

# List all utilisateurs
@login_required
@user_passes_test(lambda user: user.is_staff and user.is_active)
def utilisateur_list(request):
    search_query = request.GET.get('search', '')
    filter_role = request.GET.get('role', '')

    # Filter users excluding superusers
    utilisateurs = Utilisateur.objects.filter(is_superuser=False)

    # Search functionality
    if search_query:
        utilisateurs = utilisateurs.filter(
            Q(nom__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(telephone__icontains=search_query)
        )

    # Filter by role
    if filter_role == 'encadrant':
        utilisateurs = utilisateurs.filter(is_encadrant=True)
    elif filter_role == 'enseignant':
        utilisateurs = utilisateurs.filter(is_enseignant=True)

    # Pagination
    paginator = Paginator(utilisateurs.order_by('date_embauche'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'utilisateur/index.html', {'utilisateurs': page_obj, 'search_query': search_query, 'filter_role': filter_role})

@login_required
@user_passes_test(is_staff_and_active)
def utilisateur_detail(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)

    context = {'utilisateur': utilisateur}

    # Si l'utilisateur est un encadrant
    if utilisateur.is_encadrant:
        filieres = Filiere.objects.filter(encadrant=utilisateur)

        filieres_avec_nb_etudiants = []
        for filiere in filieres:
            # Compter les étudiants dans chaque groupe de cette filière
            groupes = Groupe.objects.filter(filiere=filiere)
            nombre_etudiants = Etudiant.objects.filter(groupe__filiere=filiere).count()

            filieres_avec_nb_etudiants.append({
                'filiere': filiere,
                'nombre_etudiants': nombre_etudiants
            })
            nombre_etudiants = Etudiant.objects.filter(groupe__filiere__encadrant=utilisateur).count()
            context['nombre_etudiants'] = nombre_etudiants

        context['filieres'] = filieres_avec_nb_etudiants

    # Si l'utilisateur est un enseignant
    if utilisateur.is_enseignant:
        modules = Module.objects.filter(enseignant=utilisateur)
        context['modules'] = modules

    return render(request, 'utilisateur/read.html', context)





@login_required
@user_passes_test(is_staff_and_active)
def create_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur créé avec succès !")
            return redirect('utilisateur_list')
        else:
            messages.error(request, "Veuillez remplir correctement tous les champs.")
    else:
        form = UtilisateurForm()

    return render(request, 'utilisateur/create.html', {'form': form})


# Update an existing utilisateur
@login_required
@user_passes_test(is_staff_and_active)
def update_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur mis à jour avec succès !")
            return redirect('utilisateur_list')
    else:
        form = UtilisateurForm(instance=utilisateur)
    return render(request, 'utilisateur/update.html', {'form': form})

# Delete an utilisateur (confirmation)
@user_passes_test(is_staff_and_active)
@login_required
def delete_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        utilisateur.delete() 
        messages.success(request, "Utilisateur supprimé avec succès !")
        return redirect('utilisateur_list')
    return render(request, 'utilisateur/delete.html', {'utilisateur': utilisateur})

# export utilisateur 
def export_utilisateurs_excel(request):
    # Create an HTTP response with the Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="utilisateurs_data.xlsx"'

    # Create an Excel workbook and select the active sheet
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Utilisateurs"

    # Define the header row in the Excel sheet
    worksheet.append(['Nom', 'Email', 'Téléphone', 'Spécialité', 'Statut', 'Compte'])

    # Write data rows to the Excel sheet excluding superusers
    utilisateurs = Utilisateur.objects.filter(is_superuser=False)  # Exclude superusers
    for utilisateur in utilisateurs:
        worksheet.append([
            utilisateur.nom,
            utilisateur.email,
            utilisateur.telephone,
            utilisateur.specialite,
            'Activé' if utilisateur.is_active else 'Désactivé',
            'Encadrant' if utilisateur.is_encadrant else 'Enseignant'
        ])

    # Save the workbook content to the response
    workbook.save(response)
    return response

# ---------------------- Views Filiere ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def filiere_list(request):
    filieres = Filiere.objects.all()
    return render(request, 'filiere/index.html', {'filieres': filieres})

@login_required
@user_passes_test(is_staff_and_active)
def filiere_detail(request, pk):
    # Get the filiere object or return a 404 error if not found
    filiere = get_object_or_404(Filiere, pk=pk)

    # Check if the connected user is an encadrant
    if not request.user.is_encadrant:
        messages.error(request, "You do not have permission to view this filière.")
        return redirect('filiere_list')

    # Check if the connected user is the encadrant of this filière
    if request.user != filiere.encadrant:
        messages.error(request, "You are only allowed to view your own filières details.")
        return redirect('filiere_list')

    # If everything checks out, render the filière details
    return render(request, 'filiere/read.html', {'filiere': filiere})


@login_required
@user_passes_test(is_staff_and_active)
def create_filiere(request):
    if request.method == 'POST':
        form = FiliereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Filière créée avec succès !")
            return redirect('filiere_list')
    else:
        form = FiliereForm()
    return render(request, 'filiere/create.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)
def update_filiere(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if request.method == 'POST':
        form = FiliereForm(request.POST, instance=filiere)
        if form.is_valid():
            form.save()
            messages.success(request, "Filière mise à jour avec succès !")
            return redirect('filiere_list')
    else:
        form = FiliereForm(instance=filiere)
    return render(request, 'filiere/update.html', {'form': form})

@user_passes_test(is_staff_and_active)
@login_required
def delete_filiere(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if request.method == 'POST':
        filiere.delete()
        messages.success(request, "Filière supprimée avec succès !")
        return redirect('filiere_list')
    return render(request, 'filiere/delete.html', {'filiere': filiere})


# ---------------------- Views Module ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def module_list(request):
    modules = Module.objects.all()
    return render(request, 'module/index.html', {'modules': modules})

@login_required
@user_passes_test(is_staff_and_active)
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    return render(request, 'module/read.html', {'module': module})

@login_required
@user_passes_test(is_staff_and_active)
def create_module(request):
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Module créé avec succès !")
            return redirect('module_list')
    else:
        form = ModuleForm()
    return render(request, 'module/create.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)
def update_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module mis à jour avec succès !")
            return redirect('module_list')
    else:
        form = ModuleForm(instance=module)
    return render(request, 'module/update.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)

def delete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, "Module supprimé avec succès !")
        return redirect('module_list')
    return render(request, 'module/delete.html', {'module': module})


# ---------------------- Views Groupe ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def groupe_list(request):
    groupes = Groupe.objects.all()
    return render(request, 'groupe/index.html', {'groupes': groupes})

@login_required
@user_passes_test(is_staff_and_active)
def groupe_detail(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    return render(request, 'groupe/read.html', {'groupe': groupe})

@login_required
@user_passes_test(is_staff_and_active)
def create_groupe(request):
    if request.method == 'POST':
        form = GroupeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Groupe créé avec succès !")
            return redirect('groupe_list')
    else:
        form = GroupeForm()
    return render(request, 'groupe/create.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)
def update_groupe(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.method == 'POST':
        form = GroupeForm(request.POST, instance=groupe)
        if form.is_valid():
            form.save()
            messages.success(request, "Groupe mis à jour avec succès !")
            return redirect('groupe_list')
    else:
        form = GroupeForm(instance=groupe)
    return render(request, 'groupe/update.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)

def delete_groupe(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.method == 'POST':
        groupe.delete()
        messages.success(request, "Groupe supprimé avec succès !")
        return redirect('groupe_list')
    return render(request, 'groupe/delete.html', {'groupe': groupe})



# ---------------------- Views Etudiant ----------------------

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Q
from django.shortcuts import render, get_object_or_404
from .models import Filiere, Groupe, Etudiant

def is_staff_and_active(user):
    return user.is_staff and user.is_active

@login_required
@user_passes_test(is_staff_and_active)
def etudiant_list(request):
    # Retrieve all available Filiere objects with associated groups
    filieres = Filiere.objects.filter(groupe__isnull=False).distinct()

    # Extract query parameters
    filiere_id = request.GET.get('filiere_id')
    groupe_id = request.GET.get('groupe_id')
    search_query = request.GET.get('search', '').strip()
    page_number = request.GET.get('page')

    # Get selected Filiere or fallback to the first available
    selected_filiere = Filiere.objects.filter(id=filiere_id).first() if filiere_id else filieres.first()

    # Get associated Groupes for the selected Filiere
    groupes = Groupe.objects.filter(filiere=selected_filiere) if selected_filiere else []

    # Get selected Groupe or fallback to the first available
    selected_groupe = Groupe.objects.filter(id=groupe_id).first() if groupe_id else groupes.first()

    # Filter Etudiants based on the selected Groupe
    etudiants = Etudiant.objects.filter(groupe=selected_groupe) if selected_groupe else Etudiant.objects.none()

    # Apply search filtering
    if search_query:
        etudiants = etudiants.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Annotate Etudiants with their average note and sort them
    etudiants = etudiants.annotate(average_note=Avg('note__note_finale')).order_by('-average_note')

    # Implement pagination
    paginator = Paginator(etudiants, 10)
    etudiants_page = paginator.get_page(page_number)

    # Select top 3 students based on their average note
    top_students = etudiants[:3] if etudiants.exists() else []

    # Context for the template
    context = {
        'filieres': filieres,
        'selected_filiere': selected_filiere,
        'groupes': groupes,
        'selected_groupe': selected_groupe,
        'etudiants': etudiants_page,
        'top_students': top_students,
        'search_query': search_query,
    }

    # Render the template
    return render(request, 'etudiant/index.html', context)


@login_required
@user_passes_test(is_staff_and_active)
def etudiant_detail(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    return render(request, 'etudiant/read.html', {'etudiant': etudiant})

@login_required
@user_passes_test(is_staff_and_active)
def create_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Étudiant créé avec succès !")
            return redirect('etudiant_list')
    else:
        form = EtudiantForm()
    return render(request, 'etudiant/create.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)    
def update_etudiant(request, pk):
        etudiant = get_object_or_404(Etudiant, pk=pk)
        if request.method == 'POST':
            form = EtudiantForm(request.POST, instance=etudiant)
            if form.is_valid():
                form.save()
                messages.success(request, "Étudiant mis à jour avec succès !")
                return redirect('etudiant_list')
        else:
            form = EtudiantForm(instance=etudiant)
        return render(request, 'etudiant/update.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)

def delete_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        etudiant.delete()
        messages.success(request, "Étudiant supprimé avec succès !")
        return redirect('etudiant_list')
    return render(request, 'etudiant/delete.html', {'etudiant': etudiant})

# ---------------------- Views Note ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def create_note(request):
    filieres = Filiere.objects.filter(groupe__isnull=False, module__isnull=False).distinct()

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Note créée avec succès !")
            return redirect('note_list')
    else:
        form = NoteForm()

    return render(request, 'note/create.html', {'form': form, 'filieres': filieres})

def get_groupes(request):
    filiere_id = request.GET.get('filiere_id')
    groupes = Groupe.objects.filter(filiere_id=filiere_id)
    data = [{"id": groupe.id, "nom": groupe.nom} for groupe in groupes]
    return JsonResponse(data, safe=False)

def get_modules(request):
    filiere_id = request.GET.get('filiere_id')
    modules = Module.objects.filter(filiere_id=filiere_id)
    data = [{"id": module.id, "nom": module.nom} for module in modules]
    return JsonResponse(data, safe=False)

def get_etudiants(request):
    groupe_id = request.GET.get('groupe_id')
    etudiants = Etudiant.objects.filter(groupe_id=groupe_id)
    data = [{"id": etudiant.id, "nom": etudiant.nom} for etudiant in etudiants]
    return JsonResponse(data, safe=False)

@login_required
@user_passes_test(is_staff_and_active)
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note mise à jour avec succès !")
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)
    return render(request, 'note/update.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note supprimée avec succès !")
        return redirect('note_list')
    return render(request, 'note/delete.html', {'note': note})

@login_required
@user_passes_test(is_staff_and_active)
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    return render(request, 'note/read.html', {'note': note})


@login_required
@user_passes_test(is_staff_and_active)
def note_list(request):
    # Obtenir toutes les filières avec groupes existants
    filieres = Filiere.objects.filter(groupe__isnull=False).distinct()

    # Sélectionner la filière (ou la première disponible)
    filiere_id = request.GET.get('filiere_id')
    selected_filiere = get_object_or_404(Filiere, id=filiere_id) if filiere_id else filieres.first()

    # Obtenir les groupes pour la filière sélectionnée
    groupes = Groupe.objects.filter(filiere=selected_filiere) if selected_filiere else []

    # Sélectionner le groupe (ou le premier disponible)
    groupe_id = request.GET.get('groupe_id')
    selected_groupe = get_object_or_404(Groupe, id=groupe_id) if groupe_id else groupes.first()

    # Obtenir les modules pour la filière sélectionnée
    modules = Module.objects.filter(filiere=selected_filiere) if selected_filiere else []

    # Sélectionner le module (ou le premier disponible)
    module_id = request.GET.get('module_id')
    selected_module = get_object_or_404(Module, id=module_id) if module_id else modules.first()

    # Obtenir les notes pour le groupe et le module sélectionnés
    notes = Note.objects.filter(
        etudiant__groupe=selected_groupe,
        module=selected_module
    ) if selected_groupe and selected_module else []

    # Contexte pour le rendu
    context = {
        'filieres': filieres,
        'selected_filiere': selected_filiere,
        'groupes': groupes,
        'selected_groupe': selected_groupe,
        'modules': modules,
        'selected_module': selected_module,
        'notes': notes,
    }

    return render(request, 'note/index.html', context)

