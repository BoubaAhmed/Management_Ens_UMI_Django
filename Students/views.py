from django.shortcuts import render, redirect
from django.contrib import messages
from ens.models import Etudiant,Note,Module

def etudiant_login(request):
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        try:
            # Authenticate using email and CNE
            etudiant = Etudiant.objects.get(email=email, password=password)
            # Store Etudiant ID in session
            request.session['etudiant_id'] = etudiant.id
            messages.success(request, f"Bienvenue, {etudiant.prenom}!")
            return redirect('etudiant_dashboard')
        except Etudiant.DoesNotExist:
            messages.error(request, "Informations de connexion invalides.")
    
    return render(request, 'students/login.html', {'title': 'Connexion Etudiant', 'user_type': 'Etudiant'})



def etudiant_dashboard(request):
    # Check if the user is logged in as Etudiant
    etudiant_id = request.session.get('etudiant_id')
    if not etudiant_id:
        return redirect('etudiant_login')

    # Get the Etudiant's details
    etudiant = Etudiant.objects.get(id=etudiant_id)

    # Get the selected semester from the GET request
    semester = request.GET.get('semester', None)

    # Fetch notes based on the semester
    if semester:
        notes = Note.objects.filter(etudiant=etudiant, module__semestre=semester)
    else:
        notes = Note.objects.filter(etudiant=etudiant)  # No filter applied

    # Get distinct semesters from the related Module model
    semesters = Module.objects.values_list('semestre', flat=True).distinct()
    if request.method == 'POST' and 'new_password' in request.POST:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                try:
                    etudiant.password = new_password
                    etudiant.save()
                    messages.success(request, "Le mot de passe a été mis à jour avec succès.")
                except Exception as e:
                    messages.error(request, f"Une erreur est survenue : {str(e)}")
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")

    return render(
        request, 
        'students/dashboard.html', 
        {'etudiant': etudiant, 'notes': notes, 'semesters': semesters, 'selected_semester': semester}
    )


def etudiant_logout(request):
    request.session.flush()  # Clear the session
    return redirect('etudiant_login')

