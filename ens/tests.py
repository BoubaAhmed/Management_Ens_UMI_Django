from django.test import TestCase
from .models import (
    Utilisateur, Filiere, Module, Groupe, Etudiant, Note
)
from django.core.exceptions import ValidationError
from decimal import Decimal
import datetime

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = Utilisateur.objects.create_user(
            email="testuser@example.com",
            password="password123",
            nom="Test",
            prenom="User",
            is_encadrant=True,
        )
        self.filiere = Filiere.objects.create(
            nom="Informatique",
            description="Filière d'informatique",
            encadrant=self.user,
        )
        self.module = Module.objects.create(
            code="INF101",
            nom="Programmation",
            description="Cours de programmation",
            filiere=self.filiere,
            enseignant=self.user,
            coefficient=3,
        )
        self.groupe = Groupe.objects.create(
            nom="G1",
            filiere=self.filiere,
        )
        self.etudiant = Etudiant.objects.create(
            nom="Student",
            prenom="Example",
            email="student@example.com",
            cni="X123456",
            cne="X123456789",
            telephone="1234567890",
            date_naissance=datetime.date(2000, 1, 1),
            adresse="123 Main St",
            annee_inscription=2023,
            groupe=self.groupe,
        )

    def test_utilisateur_creation(self):
        user = Utilisateur.objects.get(email="testuser@example.com")
        self.assertEqual(user.nom, "Test")
        self.assertTrue(user.is_encadrant)

    def test_filiere_creation(self):
        filiere = Filiere.objects.get(nom="Informatique")
        self.assertEqual(filiere.encadrant, self.user)

    def test_module_creation(self):
        module = Module.objects.get(code="INF101")
        self.assertEqual(module.nom, "Programmation")
        self.assertEqual(module.filiere, self.filiere)

    def test_groupe_creation(self):
        groupe = Groupe.objects.get(nom="G1")
        self.assertEqual(groupe.filiere, self.filiere)

    def test_etudiant_creation(self):
        etudiant = Etudiant.objects.get(email="student@example.com")
        self.assertEqual(etudiant.nom, "Student")
        self.assertEqual(etudiant.groupe, self.groupe)

    def test_etudiant_cni_validation(self):
        with self.assertRaises(ValidationError):
            invalid_etudiant = Etudiant(
                nom="Invalid",
                prenom="CNI",
                email="invalid@example.com",
                cni="INVALID123",  # Invalid CNI format
                cne="X123456789",
                telephone="1234567890",
                date_naissance=datetime.date(2000, 1, 1),
                adresse="123 Main St",
                annee_inscription=2023,
                groupe=self.groupe,
            )
            invalid_etudiant.full_clean()

    def test_note_creation(self):
        note = Note.objects.create(
            etudiant=self.etudiant,
            module=self.module,
            note_ds=15,
            note_tp=14,
            note_exam=16,
        )
        expected_final = (
            (Decimal('15') * Decimal('0.3')) +
            (Decimal('14') * Decimal('0.2')) +
            (Decimal('16') * Decimal('0.5'))
        )
        self.assertEqual(note.note_finale, expected_final)

    def test_duplicate_notes(self):
        Note.objects.create(
            etudiant=self.etudiant,
            module=self.module,
            note_ds=15,
            note_tp=14,
            note_exam=16,
        )
        with self.assertRaises(Exception):  # Unique constraint violation
            Note.objects.create(
                etudiant=self.etudiant,
                module=self.module,
                note_ds=12,
                note_tp=13,
                note_exam=14,
            )
