# admin.py
from django.contrib import admin
from .models import Utilisateur, Etudiant, Module, Filiere, Groupe , Note
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden

admin.site.site_header = "Master Umi"
admin.site.site_title = "MyApp Admin Portal"
admin.site.index_title = "Welcome to MyApp Admin"

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    model = Utilisateur
    list_display = ('email', 'nom', 'prenom', 'date_embauche',  'is_superuser', 'date_embauche')
    list_filter = ('email', 'nom', 'date_embauche')
    search_fields = ('email', 'nom', 'prenom')  # Include related field search
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')  # Use read-only for timestamps

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('nom', 'prenom',  'telephone', 'adresse','image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','is_encadrant', 'is_enseignant')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),  # Include read-only fields
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),  # Password1/2 for user creation
        ('Personal Info', {'fields': ('nom', 'prenom', 'telephone' ,'image',  'adresse', 'specialite', 'statut', 'annee_inscription')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser','is_encadrant', 'is_enseignant')}),
    )

    def has_change_permission(self, request, obj=None):
        if obj is None:  # General permission check for list view
            return True
        if obj == request.user:
            return True  # Allow users to edit their own account
        if request.user.is_superuser and not obj.is_superuser:
            return True  # Allow superusers to edit non-superusers
        return False

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        if obj == request.user:
            return True  # Allow users to delete their own account
        if obj.is_superuser:
            return False  # Prevent deletion of superusers
        return super().has_delete_permission(request, obj)

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")

    activate_users.short_description = "Activate selected users"
    deactivate_users.short_description = "Deactivate selected users"

    actions = [activate_users, deactivate_users]  

# ------------------ Groupe Admin ------------------
@admin.register(Groupe)
class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'filiere')
    search_fields = ('nom', 'filiere__nom')
    list_filter = ('filiere',)
    ordering = ('nom',)

    fieldsets = (
        (None, {'fields': ('nom', 'filiere')}),
    )

# ------------------ Etudiant Admin ------------------
@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'groupe', 'cni', 'statut', 'annee_inscription')
    search_fields = ('nom', 'prenom', 'email', 'cni')
    list_filter = ('groupe', 'statut', 'annee_inscription')
    ordering = ('nom',)

    fieldsets = (
        (None, {'fields': ('nom', 'prenom', 'email', 'telephone', 'adresse')}),
        ('Academic Info', {'fields': ('groupe', 'annee_inscription', 'statut')}),
        ('Identification Details', {'fields': ('cni', 'cne')}),
    )

# ------------------ Note Admin ------------------
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'module', 'note_ds', 'note_tp', 'note_exam', 'note_finale')
    search_fields = ('etudiant__nom', 'module__nom')
    list_filter = ('module', 'etudiant')
    ordering = ('-note_finale',)

    fieldsets = (
        (None, {'fields': ('etudiant', 'module')}),
        ('Grades', {'fields': ('note_ds', 'note_tp', 'note_exam', 'note_finale')}),
    )

# ------------------ Module Admin ------------------
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'filiere', 'enseignant', 'semestre')
    search_fields = ('code', 'nom', 'enseignant__nom')
    list_filter = ('filiere', 'semestre')
    ordering = ('code',)

    fieldsets = (
        (None, {'fields': ('code', 'nom', 'filiere')}),
        ('Instructor Info', {'fields': ('enseignant', 'description')}),
        ('Academic Details', {'fields': ('semestre', 'coefficient')}),
    )

# ------------------ Filiere Admin ------------------
from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Filiere, Utilisateur

class EncadrantListFilter(admin.SimpleListFilter):
    title = 'Encadrant'
    parameter_name = 'encadrant'

    def lookups(self, request, model_admin):
        try:
            encadrant_group = Group.objects.get(name='encadrants')
            encadrants = Utilisateur.objects.filter(groups=encadrant_group)
            return [(user.id, user) for user in encadrants]
        except Group.DoesNotExist:
            return []

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(encadrant__id=value)
        return queryset

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'encadrant')
    search_fields = ('nom', 'encadrant__nom', 'description')
    ordering = ('nom',)

    fieldsets = (
        (None, {'fields': ('nom',)}),
        ('Details', {'fields': ('description', 'encadrant')}),    
    )

    list_filter = (EncadrantListFilter,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "encadrant":
            try:
                encadrant_group = Group.objects.get(name='encadrants')
                kwargs["queryset"] = Utilisateur.objects.filter(groups=encadrant_group)
            except Group.DoesNotExist:
                kwargs["queryset"] = Utilisateur.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
