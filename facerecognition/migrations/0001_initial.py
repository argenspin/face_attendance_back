# Generated by Django 4.1.3 on 2023-03-26 18:49

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(max_length=50)),
                ('register_complete', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AcademicBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='StudClass',
            fields=[
                ('stud_class_name', models.CharField(max_length=30, primary_key=True, serialize=False, unique=True)),
                ('is_lab', models.BooleanField(default=False)),
                ('current_batch', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_batch', to='facerecognition.academicbatch')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TimeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monday', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=5)),
                ('tuesday', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=5)),
                ('wednesday', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=5)),
                ('thursday', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=5)),
                ('friday', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=5)),
                ('stud_class_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timetable_class_name', to='facerecognition.studclass', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_lab', models.BooleanField(default=False)),
                ('lab_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lab_name', to='facerecognition.studclass')),
                ('stud_class_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='class_name', to='facerecognition.studclass')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('register_no', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('dob', models.DateField(blank=True, default=datetime.date(2023, 3, 27), null=True)),
                ('face_photo_b64', models.TextField(blank=True, default='', null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_batch', to='facerecognition.academicbatch')),
                ('stud_class_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facerecognition.studclass')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('subject1_att', models.BooleanField(default=False)),
                ('subject2_att', models.BooleanField(default=False)),
                ('subject3_att', models.BooleanField(default=False)),
                ('subject4_att', models.BooleanField(default=False)),
                ('subject5_att', models.BooleanField(default=False)),
                ('stud_class_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_class_name', to='facerecognition.studclass')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_id', to='facerecognition.student')),
            ],
        ),
    ]
