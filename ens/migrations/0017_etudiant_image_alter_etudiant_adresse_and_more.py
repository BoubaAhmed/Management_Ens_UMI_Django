# Generated by Django 5.1.3 on 2024-12-15 19:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0016_etudiant_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='etudiant',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='static/Assets/profiles/etudiants/'),
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='adresse',
            field=models.TextField(default='meknes'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='date_naissance',
            field=models.DateField(default=datetime.datetime(2024, 12, 15, 19, 32, 26, 217809, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='password',
            field=models.CharField(default='15F3Wt9e', max_length=128),
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='telephone',
            field=models.CharField(default='0000000000', max_length=20),
        ),
    ]
