from django.db import models
from datetime import date
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class TeacherUser(AbstractUser):

    id = models.AutoField(primary_key=True,auto_created=True)
    name = models.CharField(max_length=50,blank=False,null=False)
    register_complete = models.BooleanField(default=False)

class AcademicBatch(models.Model):
    batch_name = models.CharField(max_length=30,null=False,blank=False)

    def __str__(self) -> str:
        return self.batch_name

class StudClass(models.Model):
    stud_class_name = models.CharField(unique=True,null=False,max_length=30,primary_key=True)
    current_batch = models.ForeignKey(AcademicBatch,on_delete=models.CASCADE,null=True,blank=True,related_name='current_batch')
    teacher = models.ForeignKey(TeacherUser,on_delete=models.CASCADE,null=True,blank=True)
    is_lab = models.BooleanField(default=False)

class Subject(models.Model):
    name = models.CharField(null=False,max_length=100)
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,blank=True,to_field='stud_class_name',related_name='class_name')
    lab_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=True,blank=True,to_field='stud_class_name',related_name="lab_name")
    is_lab = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class Student(models.Model):
    name = models.CharField(null=False,max_length=30)
    register_no = models.CharField(max_length=15,null=True,blank=True,unique=True)
    dob = models.DateField(null=True,blank=True,default=date.today())
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,null=False,to_field='stud_class_name')
    batch = models.ForeignKey(AcademicBatch,on_delete=models.CASCADE,null=False,related_name='student_batch')
    face_photo_b64 = models.TextField(default='',blank=True,null=True)

    def __str__(self):
        return self.name + ' - ' + self.stud_class_name.stud_class_name

class TimeTable(models.Model):
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,unique=True,to_field='stud_class_name',related_name="timetable_class_name")
    monday = ArrayField(models.IntegerField(),size=5,null=True)
    tuesday = ArrayField(models.IntegerField(),size=5,null=True)
    wednesday = ArrayField(models.IntegerField(),size=5,null=True)
    thursday = ArrayField(models.IntegerField(),size=5,null=True)
    friday = ArrayField(models.IntegerField(),size=5,null=True)

    def __str__(self):
        return self.stud_class_name.stud_class_name + 'TimeTable'

class Attendance(models.Model):
    stud_class_name = models.ForeignKey(StudClass,on_delete=models.CASCADE,to_field='stud_class_name',related_name="attendance_class_name",null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE,to_field='id',related_name='student_id',null=False)
    date = models.DateField(null=False)
    subject1_att = models.BooleanField(default=False)
    subject2_att = models.BooleanField(default=False)
    subject3_att = models.BooleanField(default=False)
    subject4_att = models.BooleanField(default=False)
    subject5_att = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.student.name + " - " + str(self.date)

