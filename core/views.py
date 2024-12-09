from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Slide, Article
from django.db.models import Count, Avg
from ens.models import Utilisateur, Etudiant, Filiere, Module, Note

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
    # User stats
    total_users = Utilisateur.objects.count()
    encadrants_count = Utilisateur.objects.filter(is_encadrant=True).count()
    enseignants_count = Utilisateur.objects.filter(is_enseignant=True).count()
    
    # Student stats
    total_students = Etudiant.objects.count()
    students_by_status = Etudiant.objects.values('statut').annotate(count=Count('id'))
    students_by_filiere = Filiere.objects.annotate(total_students=Count('groupe__etudiant'))
    
    # Module stats
    total_modules = Module.objects.count()
    modules_by_semester = Module.objects.values('semestre').annotate(count=Count('id'))
    
    # Notes and performance
    avg_notes_per_module = Note.objects.values('module__nom').annotate(avg_finale=Avg('note_finale'))
    
    # Content stats
    total_slides = Slide.objects.count()
    total_articles = Article.objects.count()
    latest_article = Article.objects.filter(is_published=True).order_by('-published_date').first()
    
    # Pass data to the template
    context = {
        'total_users': total_users,
        'encadrants_count': encadrants_count,
        'enseignants_count': enseignants_count,
        'total_students': total_students,
        'students_by_status': students_by_status,
        'students_by_filiere': students_by_filiere,
        'total_modules': total_modules,
        'modules_by_semester': modules_by_semester,
        'avg_notes_per_module': avg_notes_per_module,
        'total_slides': total_slides,
        'total_articles': total_articles,
        'latest_article': latest_article,
    }
    return render(request, 'core/dashboard.html', context)
