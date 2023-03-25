from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import TeacherUser,Student,StudClass
from django.contrib.auth import get_user_model
from .models import TeacherUser,StudClass,Subject,Attendance,AcademicBatch

User = get_user_model()

#Function to find the stud_class of a teacher
def findTeachersStudClass(user_id):
    try:
        stud_class_obj = StudClass.objects.get(teacher=user_id)
        if(stud_class_obj.teacher):
            print("teacher's id = ")
            print(stud_class_obj.teacher)
            return stud_class_obj.stud_class_name
    except:
        pass
    return None

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls,user):
        token = super(MyTokenObtainPairSerializer,cls).get_token(user)
        token['stud_class_name'] = 'Not Assigned'
        try:
            teacher_obj = TeacherUser.objects.get(id=token['user_id'])
            stud_class_name = findTeachersStudClass(token['user_id'])
            if(stud_class_name):
                token['stud_class_name'] = stud_class_name
            print(stud_class_name)
            if(teacher_obj.is_staff == False):
                token['user_type'] = 'teacher'
                return token
        except:
            pass
        token['user_type'] = 'admin'
        token['stud_class_name'] = 'all'
        return token
class TeacherUserCreateSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required = True)
    name = serializers.CharField(required=True)
    
    class Meta:
        model = TeacherUser
        fields = ('email','username','name')
    def create(self, validated_data):
        default_password = "12345678"
        instance = self.Meta.model(**validated_data) #Create a new serializer obj with current validated_data
        if default_password is not None:
            instance.set_password(default_password) #Set hashed password to user instance

        instance.save() #Save serializer data to database (User created)
        print("Default Password is : "+default_password)
        return instance

class TeacherCompleteRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required = True)
    name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    class Meta:
        model = TeacherUser
        fields = ('username','name','password')


class TeacherEditSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required = True)
    name = serializers.CharField(required=True)
    # subject = serializers.CharField(required=True)
    class Meta:
        model = TeacherUser
        fields = ['username','name']

class TeacherRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherUser
        fields = ['id','name','username','is_staff']


#Serializer to also include teacher name in retrieving stud_classes
class StudClassForClassesSerializer(serializers.ModelSerializer):
    batch_name = serializers.SerializerMethodField(method_name='get_batch_name') #batch name
    teacher_name = serializers.SerializerMethodField(method_name='get_teacher_name') #teacher name
    def get_teacher_name(self,studclassobj):
        try:
            teacher_name = TeacherUser.objects.get(username=studclassobj.teacher).name

        except:
            teacher_name = ''
        return teacher_name
    
    def get_batch_name(self,studclassobj):
        try:
            batch_name = studclassobj.current_batch.batch_name
        except:
            batch_name = ''
        return batch_name
    class Meta:
        model = StudClass
        fields = ['stud_class_name','teacher','teacher_name','is_lab','current_batch','batch_name']

class StudClassRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudClass
        fields = ['teacher']

class LabStudClassRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudClass
        fields = ['stud_class_name','teacher','is_lab']

class StudClassSerializer(serializers.ModelSerializer):
    batch_name = serializers.SerializerMethodField(method_name='get_batch_name') #batch name
    def get_batch_name(self,studclassobj):
        try:
            batch_name = studclassobj.current_batch.batch_name
        except:
            batch_name = ''
        return batch_name

    class Meta:
        model = StudClass
        fields = ['stud_class_name','teacher','is_lab','current_batch','batch_name']

class StudClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudClass
        fields = ['stud_class_name','is_lab','current_batch']

class StudentSerializer(serializers.ModelSerializer):
    
    batch_name = serializers.SerializerMethodField(method_name='get_batch_name') #teacher name
    def get_batch_name(self,studentobj):
        try:
            batch_name = studentobj.batch.batch_name
        except:
            batch_name = ''
        return batch_name
    class Meta:
        model = Student
        fields = ['id','name','dob','stud_class_name','register_no','dob','batch','batch_name']


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id','name','stud_class_name','face_photo_b64', 'register_no','dob','batch']

class StudentEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    register_no = serializers.CharField()
    class Meta:
        model = Student
        fields = ['id','name','stud_class_name','face_photo_b64','register_no','dob','batch']

class ClassSubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','name','stud_class_name','lab_name','is_lab']

class ClassSubjectsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','name','stud_class_name','lab_name','is_lab']

class ClassSubjectEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    stud_class_name = serializers.CharField(required=True)
    lab_name = serializers.CharField(required=True)
    class Meta:
        model = Subject
        fields = ['id','name','stud_class_name','lab_name']

class AttendanceRetrieveSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(method_name='get_student_name') #student name
    def get_student_name(self,attendance_obj):
        student_name = attendance_obj.student.name
        return student_name
    
    batch_name = serializers.SerializerMethodField(method_name='get_batch_name') #batch name
    def get_batch_name(self,attendanceobj):
        try:
            batch_name = attendanceobj.student.batch.batch_name
        except:
            batch_name = ''
        return batch_name
    
    batch = serializers.SerializerMethodField(method_name='get_batch') #batch name
    def get_batch(self,attendanceobj):
        batch = attendanceobj.student.batch.id
        return batch
    
    register_no = serializers.SerializerMethodField(method_name='get_register_no')
    def get_register_no(self,attendanceobj):
        register_no = attendanceobj.student.register_no
        return register_no
    
    class Meta:
        model = Attendance
        fields = ['id','stud_class_name','student','student_name','date',
                  'subject1_att','subject2_att','subject3_att','subject4_att','subject5_att',
                  'batch_name','batch','register_no'
                  ]

class AcademicBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicBatch
        fields = ['id','batch_name']

