# Generated by Django 4.1.3 on 2022-12-24 15:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facerecognition', '0005_rename_stud_class_student_stud_class_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='dob',
            field=models.DateField(default=datetime.date(2022, 12, 24), null=True),
        ),
    ]