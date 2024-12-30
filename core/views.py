from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Slide, Article
from django.db.models import Count, Avg
from ens.models import Utilisateur, Etudiant, Filiere, Module, Note, Groupe
from django.db.models import Count, Avg,Max, Sum, F
from datetime import datetime

def home_view(request):
    slides = Slide.objects.all()
    if not slides.exists():
        slides = [
            {
                "image": "/static/Assets/slides/slide1.jpg",
                "title": "Default Slide 1",
                "description": "This is a default slide."
            },
            {
                "image": "/static/Assets/slides/slide2.jpg",
                "title": "Default Slide 2",
                "description": "Another default slide."
            },
            {
                "image": "/static/Assets/slides/slide3.jpg",
                "title": "Default Slide 3",
                "description": "Fallback content."
            }
        ]
    articles = Article.objects.filter(is_published=True).order_by('-published_date')[:8]
    if not articles.exists():
        articles = [
            {
                "image": "/static/Assets/slides/slide1.jpg",
                "title": "Default Article 1",
                "description": "This is a default Article."
            },
            {
                "image": "/static/Assets/slides/slide2.jpg",
                "title": "Default Article 2",
                "description": "Another default Article."
            },
            {
                "image": "/static/Assets/slides/slide3.jpg",
                "title": "Default Article 3",
                "description": "Fallback content."
            }
        ]
    return render(request, 'core/home.html', {'slides': slides ,'articles': articles})

def articles_view(request):
    articles = Article.objects.all()
    return render(request, 'articles.html', {'articles': articles})



@login_required
def dashboard_view(request):
    # ---------------------- Statistiques des utilisateurs ----------------------
    total_users = Utilisateur.objects.filter(is_superuser=False).count()
    encadrants_count = Utilisateur.objects.filter(is_encadrant=True).count()
    enseignants_count = Utilisateur.objects.filter(is_enseignant=True, is_encadrant=False).count()
    total_modules = Module.objects.count()

    # ---------------------- Statistiques des étudiants ----------------------
    total_students = Etudiant.objects.count()
    students_by_status = Etudiant.objects.values('statut').annotate(count=Count('id'))

    # Get the number of students and users per year (last 5 years)
    current_year = datetime.now().year
    years = [current_year - i for i in range(5)]

    students_per_year = []
    for year in years:
        students_per_year.append(
            Etudiant.objects.filter(created_at__year=year).count()
        )

    users_per_year = []
    for year in years:
        users_per_year.append(
            Utilisateur.objects.filter(created_at__year=year, is_superuser=False).count()
        )

    new_students = Etudiant.objects.filter(created_at__year=current_year).count()
    student_Suspended = Etudiant.objects.filter(statut='suspendu',created_at__year=current_year).count()
    # ---------------------- Top-performing students by Filière ----------------------
    top_five_etudiants = Etudiant.objects.annotate(
        total_grade=Sum(F('note__note_finale'))
    ).order_by('-total_grade')[:5]

    # ---------------------- Statistiques des Modules ----------------------
    # ---------------------- Filtrer par Semestre ----------------------
    semester_filter = request.GET.get('semester', None)
    if semester_filter:
        modules_by_semester_by_filiere = (
            Module.objects.filter(semestre=semester_filter)
            .values('semestre', 'filiere__nom')
            .annotate(module_count=Count('id'))
            .order_by('semestre', 'filiere__nom')
        )
    else:
        modules_by_semester_by_filiere = (
            Module.objects.values('semestre', 'filiere__nom')
            .annotate(module_count=Count('id'))
            .order_by('semestre', 'filiere__nom')
        )

    # ---------------------- Moyennes des Notes et Performance ----------------------
    avg_notes_per_module = (
        Note.objects.values('module__id', 'module__nom', 'module__filiere__nom')
        .annotate(avg_finale=Avg('note_finale'))
        .order_by('module__nom')
    )

    # Format avg_finale to two decimal places
    avg_notes_per_module = [
        {
            'module_id': note['module__id'],
            'module_nom': note['module__nom'],
            'module_filiere_nom': note['module__filiere__nom'],
            'avg_finale': f"{note['avg_finale']:.2f}" if note['avg_finale'] is not None else None,
        }
        for note in avg_notes_per_module
    ]
    print(avg_notes_per_module)
    filiere_statistics = Filiere.objects.annotate(student_count=Count('groupe__etudiant'))

    # ---------------------- Autres statistiques ----------------------
    total_filiere = Filiere.objects.count()
    semestres = Module.objects.values_list('semestre', flat=True).distinct()

    context = {
        'total_users': total_users,
        'encadrants_count': encadrants_count,
        'enseignants_count': enseignants_count,
        'total_students': total_students,
        'students_by_status': list(students_by_status),
        'modules_by_semester_by_filiere': modules_by_semester_by_filiere,
        'avg_notes_per_module': list(avg_notes_per_module),
        'filiere_statistics': filiere_statistics,
        'total_filiere': total_filiere,
        'semestres': semestres,
        'top_five_etudiants': top_five_etudiants,
        'students_per_year': students_per_year,
        'users_per_year': users_per_year,
        'years': years, 
        'student_Suspended': student_Suspended,
        'total_modules': total_modules,
        'new_students': new_students
    }

    return render(request, 'core/dashboard.html', context)
