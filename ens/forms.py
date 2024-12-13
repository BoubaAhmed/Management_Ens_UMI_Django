from django import forms
from .models import Utilisateur, Filiere, Module, Groupe, Etudiant, Note
from django.core.exceptions import ValidationError


# ------------------ Formulaire Utilisateur ------------------
class UtilisateurForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control shadow', 'placeholder': 'Password'}),
        max_length=128,
        required=True,
        min_length=8,
    )
    class Meta:
        model = Utilisateur
        fields = ['nom', 'prenom', 'email', 'password', 'telephone', 'adresse', 'specialite', 'statut', 'is_active', 'is_staff', 'is_encadrant', 'is_enseignant','image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control shadow ', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control shadow ', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control shadow ', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control shadow', 'placeholder': 'Téléphone'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control shadow ', 'placeholder': 'Adresse'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control shadow ', 'placeholder': 'Spécialité'}),
            'statut': forms.Select(attrs={'class': 'form-control shadow '}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_encadrant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_enseignant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control shadow'}),  
        }
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Validation de la longueur et des caractères spéciaux
        if len(password) < 8:
            raise ValidationError('Le mot de passe doit avoir au moins 8 caractères.')

        if not any(char.isdigit() for char in password):
            raise ValidationError('Le mot de passe doit contenir au moins un chiffre.')

        if not any(char.isalpha() for char in password):
            raise ValidationError('Le mot de passe doit contenir au moins une lettre.')

        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for char in password):
            raise ValidationError('Le mot de passe doit contenir au moins un caractère spécial.')

        return password

# ------------------ Formulaire Filière ------------------
class FiliereForm(forms.ModelForm):
    class Meta:
        model = Filiere
        fields = ['nom', 'description', 'encadrant']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la Filière'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
            'encadrant': forms.Select(attrs={'class': 'form-control'}),
        }


# ------------------ Formulaire Module ------------------
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['semestre', 'coefficient', 'filiere', 'enseignant', 'code', 'nom', 'description']
        widgets = {
            'semestre': forms.Select(attrs={'class': 'form-control'}),
            'coefficient': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code Module'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du Module'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Description'}),
        }


# ------------------ Formulaire Groupe ------------------
class GroupeForm(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ['nom', 'filiere']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du Groupe'}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
        }


# ------------------ Formulaire Etudiant ------------------
class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'email', 'groupe', 'cni', 'cne', 'telephone', 'date_naissance', 'adresse', 'annee_inscription', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'groupe': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Groupe'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'cni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNI'}),
            'cne': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CNE'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Adresse'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'annee_inscription': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Année'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['etudiant', 'module', 'note_ds', 'note_tp', 'note_exam']
        widgets = {
            'etudiant': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'module': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'note_ds': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'DS'}),
            'note_tp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'TP'}),
            'note_exam': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Exam'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        note_ds = cleaned_data.get('note_ds')
        note_tp = cleaned_data.get('note_tp')
        note_exam = cleaned_data.get('note_exam')

        for field, value in [('DS', note_ds), ('TP', note_tp), ('Exam', note_exam)]:
            if value is not None and (value < 0 or value > 20):
                raise forms.ValidationError(f"La note pour {field} doit être entre 0 et 20.")

        return cleaned_data
