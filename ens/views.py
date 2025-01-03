from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Utilisateur, Filiere, Module, Groupe, Etudiant, Note
from .forms import (
    UtilisateurForm, FiliereForm, ModuleForm, GroupeForm, EtudiantForm, NoteForm
)
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from openpyxl import Workbook
from django.contrib import messages
from django.core.mail import send_mail
import random, string
from django.db.models import Avg, Q
import csv

def is_staff_and_active(view_func):
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

def is_encadrant(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Get the user id from URL kwargs
        if request.user.is_authenticated:
            if str(request.user.id) == str(user_id):
                # If the user is accessing their own account, let them pass
                return view_func(request, *args, **kwargs)
            
            if not hasattr(request.user, 'is_encadrant') or not request.user.is_encadrant:
                messages.error(request, "You do not have the required permissions as an encadrant.")
                return redirect('/dashboard/')
        else:
            messages.error(request, "You must log in first.")
            return redirect('/login')

        return view_func(request, *args, **kwargs)

    return wrapper

def is_enseignant(view_func):
    def wrapper(request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Get the user id from URL kwargs
        if request.user.is_authenticated:
            if str(request.user.id) == str(user_id):
                # If the user is accessing their own account, let them pass
                return view_func(request, *args, **kwargs)
            
            if not hasattr(request.user, 'is_enseignant') or not request.user.is_enseignant:
                messages.error(request, "You do not have the required permissions as an enseignant.")
                return redirect('/dashboard/')
        else:
            messages.error(request, "You must log in first.")
            return redirect('/login')

        return view_func(request, *args, **kwargs)

    return wrapper


# ---------------------- Views Utilisateur ----------------------

# List all utilisateurs
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

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

    # Password Change Form
    password_form = None
    if request.user.is_authenticated:  # Ensure user is logged in
        if request.method == 'POST' and 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('utilisateur_list')  # Adjust redirection as needed
        else:
            password_form = PasswordChangeForm(request.user)

    return render(request, 'utilisateur/index.html', {
        'utilisateurs': page_obj,
        'search_query': search_query,
        'filter_role': filter_role,
        'password_form': password_form,
    })

@login_required
@is_encadrant
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

# Generate a random password
def generate_password(): 
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@login_required
@is_encadrant
@user_passes_test(is_staff_and_active)
def create_utilisateur(request):
    if request.method == 'POST':
        form = UtilisateurForm(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save(commit=False)
            print(utilisateur)
            # Generate and set a password
            password = generate_password()
            utilisateur.set_password(password)  # Hash the password
            print(utilisateur)
            # Save the instance to the database first
            utilisateur.save()

            # Send the email with the generated password
            send_mail(
                'Votre mot de passe',
                f'Votre mot de passe temporaire est: {password}',
                'noreply@votresite.com',
                [utilisateur.email]
            )

            messages.success(request, "Utilisateur créé avec succès ! Un email a été envoyé.")
            return redirect('utilisateur_list')
        else:
            messages.error(request, "Veuillez remplir correctement tous les champs.")
    else:
        form = UtilisateurForm()

    return render(request, 'utilisateur/create.html', {'form': form})

# Update an existing utilisateur with reset password option
@login_required
@is_encadrant
@user_passes_test(is_staff_and_active)
def update_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        if 'reset_password' in request.POST:
            # Generate a new password
            new_password = generate_password()
            utilisateur.set_password(new_password)
            utilisateur.save()

            # Send email with the new password
            send_mail(
                'Réinitialisation du mot de passe',
                f'Votre mot de passe a été réinitialisé. Nouveau mot de passe: {new_password}',
                'noreply@votresite.com',
                [utilisateur.email]
            )
            messages.success(request, "Mot de passe réinitialisé avec succès.")
            return redirect('utilisateur_list')

        # For regular form updates
        form = UtilisateurForm(request.POST, request.FILES, instance=utilisateur)
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
@is_encadrant
def delete_utilisateur(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        utilisateur.delete() 
        messages.success(request, "Utilisateur supprimé avec succès !")
        return redirect('utilisateur_list')
    return render(request, 'utilisateur/delete.html', {'utilisateur': utilisateur})

# export utilisateur 
@is_encadrant
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
    # Get search query and filters from request
    search_query = request.GET.get('search', '')
    encadrant_filter = request.GET.get('encadrant', '')

    # Get all Filières and apply search query
    filieres = Filiere.objects.all()

    if search_query:
        filieres = filieres.filter(nom__icontains=search_query)

    if encadrant_filter:
        filieres = filieres.filter(encadrant__nom__icontains=encadrant_filter)

    # Annotate each Filiere with the number of Etudiants, Groupes, and Modules
    filieres_data = []
    for fil in filieres:
        num_etudiants = Etudiant.objects.filter(groupe__filiere=fil).count()
        num_groupes = Groupe.objects.filter(filiere=fil).count()
        num_modules = Module.objects.filter(filiere=fil).count()

        filieres_data.append({
            'filiere': fil,
            'nombre_etudiants': num_etudiants,
            'nombre_groupes': num_groupes,
            'num_modules': num_modules
        })

    # Pagination setup
    paginator = Paginator(filieres_data, 5)  # 5 items per page
    page = request.GET.get('page')
    paginated_filieres = paginator.get_page(page)

    return render(request, 'filiere/index.html', {
        'filieres_data': paginated_filieres,
        'search_query': search_query,
        'encadrant_filter': encadrant_filter
    })

@login_required
@user_passes_test(is_staff_and_active)
def filiere_detail(request, pk):
    # Get the filiere object or return a 404 error if not found
    filiere = get_object_or_404(Filiere, pk=pk)
    # If everything checks out, render the filière details
    return render(request, 'filiere/read.html', {'filiere': filiere})

@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
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
    if not request.user.is_encadrant:
        messages.error(request, "You do not have permission to edit this filière.")
        return redirect('filiere_list')

    if request.user != filiere.encadrant:
        messages.error(request, "You are only allowed to edit your own filières details.")
        return redirect('filiere_list')
    
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
@is_encadrant
def delete_filiere(request, pk):
    filiere = get_object_or_404(Filiere, pk=pk)
    if request.user != filiere.encadrant:
        messages.error(request, "You are only allowed to delete your own filières details.")
        return redirect('filiere_list')
    if request.method == 'POST':
        filiere.delete()
        messages.success(request, "Filière supprimée avec succès !")
        return redirect('filiere_list')
    return render(request, 'filiere/delete.html', {'filiere': filiere})


# ---------------------- Views Module ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def module_list(request):
    # Get search query and filters from request
    search_query = request.GET.get('search', '')
    semestre_filter = request.GET.get('semestre', '')
    filiere_filter = request.GET.get('filiere', '')

    # Get all Modules and apply search query
    modules = Module.objects.all()

    if search_query:
        modules = modules.filter(nom__icontains=search_query)

    if semestre_filter:
        modules = modules.filter(semestre=semestre_filter)

    if filiere_filter:
        modules = modules.filter(filiere__nom__icontains=filiere_filter)

    # Annotate each module with the number of enrolled students
    modules_data = []
    for module in modules:
        num_etudiants = Note.objects.filter(module=module).values('etudiant').distinct().count()

        modules_data.append({
            'module': module,
            'nombre_etudiants': num_etudiants,
            'filiere': module.filiere.nom,
            'semestre': module.semestre
        })

    # Pagination setup
    paginator = Paginator(modules_data, 5)  # 5 modules per page
    page = request.GET.get('page')
    paginated_modules = paginator.get_page(page)

    return render(request, 'module/index.html', {
        'modules_data': paginated_modules,
        'search_query': search_query,
        'semestre_filter': semestre_filter,
        'filiere_filter': filiere_filter
    })

@login_required
@user_passes_test(is_staff_and_active)
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    return render(request, 'module/read.html', {'module': module})

@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
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
@is_encadrant
def update_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.user != module.filiere.encadrant:
        messages.error(request, "You are only allowed to update your own filières modules.")
        return redirect('module_list')
    
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
@is_encadrant
def delete_module(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.user != module.filiere.encadrant:
        messages.error(request, "You are only allowed to delete your own filières modules.")
        return redirect('module_list')
    
    if request.method == 'POST':
        module.delete()
        messages.success(request, "Module supprimé avec succès !")
        return redirect('module_list')
    return render(request, 'module/delete.html', {'module': module})


# ---------------------- Views Groupe ----------------------

@login_required
@user_passes_test(is_staff_and_active)
def groupe_list(request):
    # Get search query and filters from request
    search_query = request.GET.get('search', '')
    filiere_filter = request.GET.get('filiere', '')

    # Get all Groupes and apply search query
    groupes = Groupe.objects.all()

    if search_query:
        groupes = groupes.filter(nom__icontains=search_query)

    if filiere_filter:
        groupes = groupes.filter(filiere__nom__icontains=filiere_filter)

    # Annotate each Groupe with the number of Etudiants
    groupes_data = []
    for groupe in groupes:
        num_etudiants = Etudiant.objects.filter(groupe=groupe).count()

        groupes_data.append({
            'groupe': groupe,
            'nombre_etudiants': num_etudiants
        })

    # Pagination setup
    paginator = Paginator(groupes_data, 5)  # 5 items per page
    page = request.GET.get('page')
    paginated_groupes = paginator.get_page(page)

    return render(request, 'groupe/index.html', {
        'groupes_data': paginated_groupes,
        'search_query': search_query,
        'filiere_filter': filiere_filter
    })

@login_required
@user_passes_test(is_staff_and_active)
def groupe_detail(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    return render(request, 'groupe/read.html', {'groupe': groupe})

@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
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
@is_encadrant
def update_groupe(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.user != groupe.filiere.encadrant:
        messages.error(request, "You are only allowed to update your own filières groupes.")
        return redirect('module_list')
    
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
@is_encadrant
def delete_groupe(request, pk):
    groupe = get_object_or_404(Groupe, pk=pk)
    if request.user != groupe.filiere.encadrant:
        messages.error(request, "You are only allowed to delete your own filières groupes.")
        return redirect('module_list')
    if request.method == 'POST':
        groupe.delete()
        messages.success(request, "Groupe supprimé avec succès !")
        return redirect('groupe_list')
    return render(request, 'groupe/delete.html', {'groupe': groupe})


# ---------------------- Views Etudiant ----------------------
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

    if request.method == 'POST' and 'change_password' in request.POST:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            try:
                # Directly update the password in the database
                etudiant.password = new_password
                etudiant.save()
                messages.success(request, "Le mot de passe a été mis à jour avec succès.")
                return redirect('etudiant_detail', pk=pk)
            except Exception as e:
                messages.error(request, f"Une erreur est survenue : {str(e)}")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")

    return render(request, 'etudiant/read.html', {'etudiant': etudiant})



@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
def create_etudiant(request):
    if request.method == 'POST':
        form = EtudiantForm(request.POST, request.FILES)
        if form.is_valid():
            etudiant = form.save(commit=False)
            email_prefix = f"{etudiant.nom[0:2].lower()}.{etudiant.prenom.lower()}"
            base_email = f"{email_prefix}@edu.umi.ac.ma"
            existing_students = Etudiant.objects.filter(email=base_email)
            if existing_students.exists():
                counter = 1
                while True:
                    new_email = f"{email_prefix}{counter}@edu.umi.ac.ma"
                    if not Etudiant.objects.filter(email=new_email).exists():
                        base_email = new_email
                        break
                    counter += 1
            etudiant.email = base_email
            password = generate_password()
            etudiant.password = password 
            if 'image' in request.FILES:
                print(f"Image uploaded: {request.FILES['image']}")
            else:
                print("No image uploaded!")
            etudiant.save()
            messages.success(request, f"Étudiant créé avec succès !")
            return redirect('etudiant_list')
    else:
        form = EtudiantForm()

    return render(request, 'etudiant/create.html', {'form': form})



@login_required
@user_passes_test(is_staff_and_active)    
@is_encadrant
def update_etudiant(request, pk):
        etudiant = get_object_or_404(Etudiant, pk=pk)
        if request.user != etudiant.groupe.filiere.encadrant:
            messages.error(request, "You are only allowed to edit your own filières students.")
            return redirect('etudiant_list')
        if request.method == 'POST':
            form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
            if form.is_valid():
                form.save()
                messages.success(request, "Étudiant mis à jour avec succès !")
                return redirect('etudiant_list')
        else:
            form = EtudiantForm(instance=etudiant)
        return render(request, 'etudiant/update.html', {'form': form})

@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
def delete_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.user != etudiant.groupe.filiere.encadrant:
            messages.error(request, "You are only allowed to delete your own filières students.")
            return redirect('etudiant_list')
    if request.method == 'POST':
        etudiant.delete()
        messages.success(request, "Étudiant supprimé avec succès !")
        return redirect('etudiant_list')
    return render(request, 'etudiant/delete.html', {'etudiant': etudiant})

# ---------------------- Views Note ----------------------

@login_required
@user_passes_test(is_staff_and_active)
@is_enseignant
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
@is_enseignant
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.user != note.module.enseignant:
            messages.error(request, "You are only allowed to edit your own  module students.")
            return redirect('etudiant_list')
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
@is_enseignant
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


@login_required
@user_passes_test(is_staff_and_active)
def assistant(request):
    return render(request, 'Assistant/chatbot.html')


@login_required
@user_passes_test(is_staff_and_active)
@is_encadrant
def download_students_accounts(request):
    group_id = request.GET.get('group_id')
    
    if not group_id:
        return redirect('etudiant_list')  # Redirect if no group_id is provided

    try:
        # Get the selected group
        groupe = Groupe.objects.get(id=group_id)
        if request.user != groupe.filiere.encadrant:
            messages.error(request, "You are only allowed to download your own filières Students.")
            return redirect('etudiant_list')
        # Filter students belonging to this group
        etudiants = Etudiant.objects.filter(groupe=groupe)

        # Create response to download CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students_accounts.csv"'

        writer = csv.writer(response)
        # Write the CSV header
        writer.writerow(['Nom', 'Prénom', 'Email', 'Mot de passe'])

        # Write each student's information
        for etudiant in etudiants:
            writer.writerow([etudiant.nom, etudiant.prenom, etudiant.email, etudiant.password])

        return response

    except Groupe.DoesNotExist:
        return redirect('etudiant_list')  # Redirect if group doesn't exist
