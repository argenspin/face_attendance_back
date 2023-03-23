# Generated by Django 4.1.3 on 2023-03-11 08:46

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facerecognition', '0008_student_register_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_name', models.CharField(max_length=15)),
            ],
        ),
        migrations.AlterField(
            model_name='student',
            name='dob',
            field=models.DateField(default=datetime.date(2023, 3, 11), null=True),
        ),
        migrations.AddField(
            model_name='studclass',
            name='current_batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_batch', to='facerecognition.academicbatch'),
        ),
    ]