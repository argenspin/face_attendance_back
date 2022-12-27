from django.db import models
from datetime import date
# Create your models here.
from django.contrib.auth.models import AbstractUser

class TeacherUser(AbstractUser):
    id = models.AutoField(primary_key=True,auto_created=True)
    name = models.CharField(max_length=50,blank=False,null=False)
    subject = models.CharField(max_length=50, blank=True,default='')
    register_complete = models.BooleanField(default=False)
    #stud_class = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,to_field='stud_class_name')
class StudClass(models.Model):
    stud_class_name = models.CharField(unique=True,null=False,max_length=30,primary_key=True)
    teacher = models.ForeignKey(TeacherUser,on_delete=models.CASCADE,null=True,blank=True)

class Student(models.Model):
    name = models.CharField(null=False,max_length=30)
    dob = models.DateField(null=True,default=date.today())
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,to_field='stud_class_name')
    face_photo_b64 = models.TextField(default='',blank=True)