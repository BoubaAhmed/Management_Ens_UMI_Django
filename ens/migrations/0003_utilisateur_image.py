# Generated by Django 5.1.3 on 2024-12-08 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0002_utilisateur_is_encadrant_utilisateur_is_enseignant'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/Assets/profiles/'),
        ),
    ]