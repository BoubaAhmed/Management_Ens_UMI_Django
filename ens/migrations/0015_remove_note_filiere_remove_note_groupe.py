# Generated by Django 5.1.3 on 2024-12-10 21:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0014_alter_note_filiere_alter_note_groupe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='filiere',
        ),
        migrations.RemoveField(
            model_name='note',
            name='groupe',
        ),
    ]