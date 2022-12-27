from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions,status
from .serializers import MyTokenObtainPairSerializer,TeacherUserCreateSerializer,StudClassSerializer,StudentSerializer,TeacherCompleteRegistrationSerializer,TeacherRetrieveSerializer,StudentCreateSerializer,StudentEditSerializer,TeacherEditSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import TeacherUser,Student,StudClass
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import requests
import json
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from . import face_check
import threading
from . view_helpers import identifyTeacherStudClass,identifyTeacherUserId,identifyUserType,register_completion_mail_send

back_url = "http://localhost:8000/api/"
front_url = "http://localhost:3000/"

User = get_user_model()


# Create your views here.
class ObtainTokenPairWithColorView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    
class TeacherUserCreate(APIView):
    permission_classes = (permissions.AllowAny),
    
    def post(self,request, format='json'):
        serializer = TeacherUserCreateSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                random_password = User.objects.make_random_password(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789')
                teacher_email = serializer.data['email']
                teacher_password = random_password
                teacher_obj = TeacherUser.objects.get(username=serializer.data['username'])
                teacher_obj.set_password(teacher_password)
                teacher_obj.save()
                #request.data = {'username':serializer.data['username'],'password': serializer.data['username'] }
                req = requests.post(back_url+'token/obtain/', data={'username':serializer.data['username'],'password':teacher_password})
                req_as_dict = json.loads(req.text)
                register_link = front_url + 'register/' + req_as_dict['refresh'] + "/" + serializer.data['username']
                mail_subject = "email: "+teacher_email + "\nPassword: "+teacher_password+"\n"+register_link
                json_data = serializer.data

                #create a seperate thread so that response object can be returned while sending the mail .(To remove delay in sending mail)
                thread = threading.Thread(target =register_completion_mail_send, args=(mail_subject,teacher_email))
                thread.start()
                print("hello gyus")
                #register_completion_mail_send(mail_subject,teacher_email)


                return Response(json_data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherUserCompleteRegistration(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [MultiPartParser,FormParser]
    def post(self, request,*args, **kwargs):
        print(request.data)
        serializer = TeacherCompleteRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            teacher = TeacherUser.objects.get(username = serializer.data['username'])
            if(teacher.register_complete == False):
                teacher.name = serializer.data['name']
                teacher.set_password(serializer.data['password'])
                teacher.register_complete = True
                teacher.save()
                return Response(serializer.data,status=status.HTTP_200_OK)

            else:
                return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherEditView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        serializer = TeacherEditSerializer(data=request.data)
        print(request.data)
        if(serializer.is_valid()):
            teacher = TeacherUser.objects.get(username = serializer.data['username'])
            teacher.name = serializer.data['name']
            teacher.subject = serializer.data['subject']
            teacher.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class BlackListRefreshView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self,request):
        print("hello")
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("blacklisted successfully")

class RetrieveTeacherUserName(APIView):
    def get(self, request, *args, **kwargs):
        user_id = identifyTeacherUserId(request)
        teacher_obj = TeacherUser.objects.get(id=user_id)
        print(teacher_obj.username)
        data = {'loggedUser': teacher_obj.username}
        return Response(data,status=status.HTTP_200_OK)
        
class TeacherRetrieveView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def get(self, request, *args, **kwargs):
        teacherFields = TeacherUser.objects.all()
        teacher_serialized = TeacherRetrieveSerializer(teacherFields,many=True)
        return Response(teacher_serialized.data)

class RetrieveUserTypeAndStudClassName(APIView):
    def get(self, request, *args, **kwargs):
        user_type = identifyUserType(request)
        stud_class_name = identifyTeacherStudClass(request)
        data = {'user_type':user_type, 'stud_class_name':stud_class_name}
        return Response(data,status=status.HTTP_200_OK)

class TeacherDeleteView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def delete(self,request, *args, **kwargs):
        words = request.headers
        if(TeacherUser.objects.get(id=words['Id'])):
            teacher_obj = TeacherUser.objects.get(id=words['Id'])
            if(teacher_obj.is_staff):
                return Response(status=status.HTTP_403_FORBIDDEN)
            teacher_obj.delete()
            return Response(status=status.HTTP_200_OK)

class StudentRetrieveView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    
    #Retrieve all students
    def get(self, request, *args, **kwargs):
        user_type = identifyUserType(request)
        if(user_type=='teacher'):
            stud_class_name = identifyTeacherStudClass(request)
            if(stud_class_name=='Not Assigned'):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                studentfields = Student.objects.filter(stud_class_name=stud_class_name)
        elif(user_type=='admin'):
            studentfields = Student.objects.all()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        student_serialized = StudentSerializer(studentfields,many=True)
        return Response(student_serialized.data,status=status.HTTP_200_OK)
class StudentCreateView(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def post(self,request):
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #id is created only after saving the student.
            student_id = serializer.data['id']
            student_stud_class = serializer.data['stud_class_name']
            filename = 'face_data/'+str(student_stud_class) + '.fac'
            face_photo_b64 = serializer.data['face_photo_b64']

            try:
                face_check.addNewStudentFace(filename,student_id,face_photo_b64)
            except:    
                student = Student.objects.get(id=serializer.data['id'])
                student.delete()
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class StudentEditView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        serializer = StudentEditSerializer(data=request.data)
        if(serializer.is_valid()):
            student_id = serializer.data['id']
            student_name = serializer.data['name']
            face_photo_b64 = serializer.data['face_photo_b64']
            
            student = Student.objects.get(id=student_id)
            #retrieve the stud_class_name of student using foreign key reference
            current_stud_class_name = student.stud_class_name.stud_class_name
            updated_stud_class_name = serializer.data['stud_class_name']
            student_stud_class = StudClass.objects.get(stud_class_name=updated_stud_class_name)

            #Update student values
            student.name = student_name
            student.stud_class_name = student_stud_class
            student.face_photo_b64 = face_photo_b64
                
            current_filename = 'face_data/'+str(current_stud_class_name) + '.fac'
            updated_filename = 'face_data/'+str(updated_stud_class_name) + '.fac'
            try:
                face_check.editStudentFace(current_filename,updated_filename,student_id,face_photo_b64)
                student.save()
                return Response(status=status.HTTP_200_OK)
            except IndexError:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class StudentDeleteView(APIView):
    def delete(self,request):
        words = request.headers
        student_id = words['Id']
        student = Student.objects.get(id=student_id)
        if(student):
            try:
                student_stud_class_name = student.stud_class_name.stud_class_name
                filename = 'face_data/'+str(student_stud_class_name) + '.fac'
                face_check.deleteStudentFace(filename,student_id)
                student.delete()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)
            






class StudClassRetrieve(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def get(self, request, *args, **kwargs):
        studclassFields = StudClass.objects.all()
        studclass_serialized = StudClassSerializer(studclassFields,many=True)
        return Response(studclass_serialized.data)
    
    def post(self, request, *args, **kwargs):
        studclass_serialized = StudClassSerializer(data=request.data)
        if(studclass_serialized.is_valid()):
            print(studclass_serialized)
            studclass_serialized.save()
            return Response(studclass_serialized.data,status=status.HTTP_201_CREATED)
        print(studclass_serialized)

        return Response(studclass_serialized.errors,status=status.HTTP_400_BAD_REQUEST)

