# Generated by Django 5.1.3 on 2024-12-15 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ens', '0020_alter_etudiant_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='etudiant',
            name='image',
            field=models.ImageField(upload_to='profiles/etudiants/'),
        ),
        migrations.AlterField(
            model_name='etudiant',
            name='password',
            field=models.CharField(default='Ddp5RZyy', max_length=128),
        ),
    ]
