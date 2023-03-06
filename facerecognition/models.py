from django.db import models
from datetime import date
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class TeacherUser(AbstractUser):

    id = models.AutoField(primary_key=True,auto_created=True)
    name = models.CharField(max_length=50,blank=False,null=False)
    # subject = models.CharField(max_length=50, blank=True,default='')
    register_complete = models.BooleanField(default=False)
    #stud_class = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,to_field='stud_class_name')

class StudClass(models.Model):
    stud_class_name = models.CharField(unique=True,null=False,max_length=30,primary_key=True)
    teacher = models.ForeignKey(TeacherUser,on_delete=models.CASCADE,null=True,blank=True,unique=True)
    is_lab = models.BooleanField(default=False)


class Subject(models.Model):

    name = models.CharField(null=False,max_length=100)
    # is_lab = models.BooleanField(default=False,null=False)
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,blank=True,to_field='stud_class_name',related_name='class_name')
    lab_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,blank=True,to_field='stud_class_name',related_name="lab_name")
    is_lab = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class Student(models.Model):
    name = models.CharField(null=False,max_length=30)
    dob = models.DateField(null=True,default=date.today())
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,to_field='stud_class_name')
    face_photo_b64 = models.TextField(default='',blank=True)

    def __str__(self):
        return self.name

class TimeTable(models.Model):
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,unique=True,to_field='stud_class_name',related_name="timetable_class_name",null=True,blank=True)
    # monday = models.ManyToManyField(Subject,related_name="monday_subjects")
    # tuesday = models.ManyToManyField(Subject,related_name="tuesday_subjects")
    # wednesday = models.ManyToManyField(Subject,related_name="wednesday_subjects")
    # thursday = models.ManyToManyField(Subject,related_name="thursday_subjects")
    # friday = models.ManyToManyField(Subject,related_name="friday_subjects")
    monday = ArrayField(models.IntegerField(),size=5,null=True)
    tuesday = ArrayField(models.IntegerField(),size=5,null=True)
    wednesday = ArrayField(models.IntegerField(),size=5,null=True)
    thursday = ArrayField(models.IntegerField(),size=5,null=True)
    friday = ArrayField(models.IntegerField(),size=5,null=True)

    def __str__(self):
        return self.stud_class_name.stud_class_name + 'TimeTable'

