# Generated by Django 5.1.3 on 2024-12-10 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0011_auto_20241210_2036'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='note',
            name='unique_note_per_etudiant_module',
        ),
        migrations.AlterUniqueTogether(
            name='note',
            unique_together={('etudiant', 'module')},
        ),
        migrations.RemoveField(
            model_name='note',
            name='filiere',
        ),
        migrations.RemoveField(
            model_name='note',
            name='groupe',
        ),
    ]
