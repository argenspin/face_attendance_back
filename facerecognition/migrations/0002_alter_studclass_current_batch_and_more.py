# Generated by Django 4.1.3 on 2023-03-14 17:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facerecognition', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studclass',
            name='current_batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_batch', to='facerecognition.academicbatch'),
        ),
        migrations.AlterField(
            model_name='studclass',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]