# Generated by Django 5.1.3 on 2024-12-15 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0017_etudiant_image_alter_etudiant_adresse_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiant',
            name='image',
            field=models.ImageField(default='kk', upload_to='Assets/profiles/etudiants/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='password',
            field=models.CharField(default='FWzxgTHr', max_length=128),
        ),
    ]
