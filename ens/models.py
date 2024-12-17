from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
import re
from decimal import Decimal
import random,string
# ------------------ Gestionnaire Utilisateur ------------------
class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email doit être défini')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# ------------------ Modèle Utilisateur ------------------
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    STATUT_CHOICES = [('actif', 'Actif'), ('retraité', 'Retraité')]

    nom = models.CharField(max_length=100, null=False, blank=False)
    prenom = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    image = models.ImageField(upload_to='static/Assets/profiles/', null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    specialite = models.CharField(max_length=100, null=True, blank=True)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    date_embauche = models.DateField(null=True, blank=True)
    annee_inscription = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    # Adding related_name to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions')

    is_encadrant = models.BooleanField(default=False, help_text="Designates whether this user is an encadrant.")
    is_enseignant = models.BooleanField(default=False, help_text="Designates whether this user is an enseignant.")

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    def clean(self):
        """
        Ensure at least one of is_encadrant or is_enseignant is True unless the user is a superuser.
        """
        if not self.is_superuser and not (self.is_encadrant or self.is_enseignant):
            raise ValidationError("A user must be either an encadrant or an enseignant (or both).")

    def save(self, *args, **kwargs):
        # Perform validation before saving
        self.clean()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nom} {self.prenom}"


# ------------------ Filière ------------------
class Filiere(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    encadrant = models.ForeignKey(Utilisateur, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.nom}'


# ------------------ Module ------------------
class Module(models.Model):
    STATUT_CHOICES = [('s1', 'Semestre 1'), ('s2', 'Semestre 2'), ('s3', 'Semestre 3'), ('s4', 'Semestre 4')]
    semestre = models.CharField(max_length=10, choices=STATUT_CHOICES, default='s1')
    coefficient = models.PositiveSmallIntegerField(null=True, blank=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.filiere} - {self.nom}'


# ------------------ Groupe ------------------
class Groupe(models.Model):
    nom = models.CharField(max_length=50)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)

    # Using constraints to ensure unique group names per Filiere
    class Meta:
        constraints = [
            UniqueConstraint(fields=['nom', 'filiere'], name='unique_groupe_per_filiere')
        ]

    def __str__(self):
        return f'{self.filiere} {self.nom}'


# ------------------ Etudiants ------------------
def validate_cni(value):
    if not re.match(r'^[A-Z]\d{6}$', value):
        raise ValidationError("Le CNI doit suivre le format : une lettre majuscule suivie de 6 chiffres (ex: X123456).")


def validate_cne(value):
    if not re.match(r'^[A-Z]\d{9}$', value):
        raise ValidationError("Le CNE doit suivre le format : une lettre majuscule suivie de 9 chiffres (ex: X123456789).")


class Etudiant(models.Model):
    STATUT_CHOICES = [('actif', 'Actif'), ('suspendu', 'Suspendu'), ('gradué', 'Gradué')]

    nom = models.CharField(max_length=100, null=False, blank=False)
    prenom = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, default=''.join(random.choices(string.ascii_letters + string.digits, k=8)))
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    cni = models.CharField(max_length=20, unique=True, validators=[validate_cni], null=False, blank=False)
    cne = models.CharField(max_length=20, unique=True, validators=[validate_cne], null=False, blank=False)
    image = models.ImageField(upload_to='static/Assets/profiles/etudiants/', null=True, blank=True)
    telephone = models.CharField(max_length=20, null=False, blank=False,  default="0000000000")  
    date_naissance = models.DateField(null=False, blank=False)
    adresse = models.TextField(null=False, blank=False)
    annee_inscription = models.PositiveSmallIntegerField()
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.telephone and not self.telephone.isdigit():
            raise ValidationError("Le champ téléphone doit contenir uniquement des chiffres.")

    def __str__(self):
        return f'{self.nom} {self.prenom}'


# ------------------ Notes ------------------
class Note(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE) 
    note_ds = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note_tp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note_exam = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note_finale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('etudiant', 'module')  # Empêcher la duplication des notes pour un étudiant et un module.

    def save(self, *args, **kwargs):
        # Calcul de la note finale uniquement si toutes les notes nécessaires sont présentes
        if self.note_ds is not None and self.note_exam is not None:
            self.note_finale = (
                (Decimal(self.note_ds) * Decimal('0.3')) +
                (Decimal(self.note_tp or 0) * Decimal('0.2')) +
                (Decimal(self.note_exam) * Decimal('0.5'))
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.etudiant} - {self.module} - {self.note_finale}"
