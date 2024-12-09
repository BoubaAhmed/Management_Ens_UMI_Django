# Generated by Django 5.1.3 on 2024-12-06 21:35

import django.db.models.deletion
import ens.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filiere',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Groupe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50)),
                ('filiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.filiere')),
            ],
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('cni', models.CharField(max_length=20, unique=True, validators=[ens.models.validate_cni])),
                ('cne', models.CharField(max_length=20, unique=True, validators=[ens.models.validate_cne])),
                ('telephone', models.CharField(blank=True, max_length=20, null=True)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('adresse', models.TextField(blank=True, null=True)),
                ('annee_inscription', models.PositiveSmallIntegerField()),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('suspendu', 'Suspendu'), ('gradué', 'Gradué')], default='actif', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groupe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.groupe')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.CharField(choices=[('s1', 'Semestre 1'), ('s2', 'Semestre 2'), ('s3', 'Semestre 3'), ('s4', 'Semestre 4')], default='s1', max_length=10)),
                ('coefficient', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('nom', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('filiere', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.filiere')),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_ds', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('note_tp', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('note_exam', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('note_finale', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('etudiant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.etudiant')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.module')),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telephone', models.CharField(blank=True, max_length=15, null=True)),
                ('adresse', models.TextField(blank=True, null=True)),
                ('specialite', models.CharField(blank=True, max_length=100, null=True)),
                ('statut', models.CharField(choices=[('actif', 'Actif'), ('retraité', 'Retraité')], default='actif', max_length=10)),
                ('date_embauche', models.DateField(blank=True, null=True)),
                ('annee_inscription', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(related_name='custom_user_groups', to='auth.group')),
                ('user_permissions', models.ManyToManyField(related_name='custom_user_permissions', to='auth.permission')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='module',
            name='enseignant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ens.utilisateur'),
        ),
        migrations.AddField(
            model_name='filiere',
            name='encadrant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ens.utilisateur'),
        ),
        migrations.AddConstraint(
            model_name='groupe',
            constraint=models.UniqueConstraint(fields=('nom', 'filiere'), name='unique_groupe_per_filiere'),
        ),
    ]