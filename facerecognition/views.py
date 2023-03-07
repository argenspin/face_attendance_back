from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions,status
from django.core import serializers
from .serializers import MyTokenObtainPairSerializer,TeacherUserCreateSerializer,StudClassSerializer,StudentSerializer,TeacherCompleteRegistrationSerializer,TeacherRetrieveSerializer,StudentCreateSerializer,StudentEditSerializer,TeacherEditSerializer,StudClassForClassesSerializer,ClassSubjectsSerializer,ClassSubjectsCreateSerializer,LabStudClassRetrieveSerializer,StudClassCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser
from .models import TeacherUser,Student,StudClass,Subject,TimeTable
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import requests
import ujson
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
import threading
from . view_helpers import identifyTeacherStudClass,identifyTeacherUserId,identifyUserType,register_completion_mail_send,getImagesToDetectFromRequest
from . import face_check

back_url = "http://localhost:8000/api/"
front_url = "http://localhost:3000/"

User = get_user_model()


# Create your views here.
class ObtainTokenPairWithColorView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    
class TeacherUserCreate(APIView):
    
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
                req_as_dict = ujson.loads(req.text)
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
            # teacher.subject = serializer.data['subject']
            teacher.save()
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


'''class BlackListRefreshView(APIView):
    def post(self,request):
        print("hello")
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("blacklisted successfully")'''

class RetrieveTeacherUserName(APIView):
    def get(self, request, *args, **kwargs):
        user_id = identifyTeacherUserId(request)
        teacher_obj = TeacherUser.objects.get(id=user_id)
        print(teacher_obj.username)
        data = {'loggedUser': teacher_obj.username}
        return Response(data,status=status.HTTP_200_OK)

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

    #To get student' face photo using id
    def post(self,request):
        student_id = request.data['id']
        try:
            student = Student.objects.get(id=student_id)
            face_photo_b64 = student.face_photo_b64
            json_data = {'face_photo_b64':face_photo_b64}
            return Response(json_data,status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class StudentCreateView(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def post(self,request):
        #print(request.data['multiple_images'])
        multiple_images = ujson.loads(request.data['multiple_images'])
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            #id is created only after saving the student.
            student_id = serializer.data['id']
            student_stud_class = serializer.data['stud_class_name']
            filename = 'face_data/'+str(student_stud_class) + '.fac'
            face_photo_b64 = serializer.data['face_photo_b64']
            
            #face_check.addNewStudentFace(student_stud_class,student_id,multiple_images)
            #return Response(serializer.data,status=status.HTTP_200_OK)
            try:
                face_check.addNewStudentFace(student_stud_class,student_id,multiple_images)
                return Response(serializer.data,status=status.HTTP_200_OK)
            except:    
                student = Student.objects.get(id=serializer.data['id'])
                student.delete()
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class StudentEditView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        multiple_images = ujson.loads(request.data['multiple_images'])
        print(len(multiple_images))
        #print(babadf)
        serializer = StudentEditSerializer(data=request.data)
        if(serializer.is_valid()):
            student_id = serializer.data['id']
            student_name = serializer.data['name']
            face_photo_b64 = serializer.data['face_photo_b64']
            
            student = Student.objects.get(id=student_id)
            #retrieve the stud_class_name of student using foreign key reference
            current_stud_class_name = student.stud_class_name.stud_class_name
            updated_stud_class_name = serializer.data['stud_class_name']
            #Get new stud_class object updating the student
            student_stud_class = StudClass.objects.get(stud_class_name=updated_stud_class_name)

            #Update student values
            student.name = student_name
            #set new student stud_class
            student.stud_class_name = student_stud_class
            student.face_photo_b64 = face_photo_b64
            try:
                face_check.editStudentFace(current_stud_class_name,updated_stud_class_name,student_id,multiple_images)
                #face_check.editStudentFace(current_filename,updated_filename,student_id,face_photo_b64)
                student.save()
                return Response(status=status.HTTP_200_OK)
            except IndexError:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class StudentDeleteView(APIView):
    def delete(self,request):
        words = request.headers
        student_id = int(words['Id'])
        student = Student.objects.get(id=student_id)
        if(student):
            try:
                student_stud_class_name = student.stud_class_name.stud_class_name
                filename = 'face_data/'+str(student_stud_class_name) + '.fac'
                #face_check.deleteStudentFace(filename,student_id)
                face_check.deleteStudentFace(student_stud_class_name,student_id)
                student.delete()
                return Response(status=status.HTTP_200_OK)
            except:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)
            

#View for 'Classes' section on frontend
class StudClassOperationsForClassesView(APIView):
    parser_classes = [MultiPartParser,FormParser]

# retrieve studclasses that are not lab
    def get(self,request):
        studclassFields = StudClass.objects.filter(is_lab=False)
        studclass_serialized = StudClassForClassesSerializer(studclassFields,many=True)
        print(studclass_serialized.data)
        return Response(studclass_serialized.data)



#View to retrieve studclasses for everywhere except 'Classes' section
class StudClassRetrieve(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def get(self, request, *args, **kwargs):
        studclassFields = StudClass.objects.all()
        studclass_serialized = StudClassForClassesSerializer(studclassFields,many=True)
        return Response(studclass_serialized.data)
    
    def post(self, request, *args, **kwargs):
        studclass_serialized = StudClassSerializer(data=request.data)
        if(studclass_serialized.is_valid()):
            print(studclass_serialized)
            studclass_serialized.save()
            return Response(studclass_serialized.data,status=status.HTTP_201_CREATED)
        print(studclass_serialized)

        return Response(studclass_serialized.errors,status=status.HTTP_400_BAD_REQUEST)

class StudClassCreateView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self, request, *args, **kwargs):
        request.data._mutable = True
        if(request.data['is_lab']=='false'):
            request.data['is_lab'] = False
        elif(request.data['is_lab']=='true'):
            request.data['is_lab'] = True
        studclass_serialized = StudClassSerializer(data=request.data)
        if(studclass_serialized.is_valid()):
            print(studclass_serialized)
            try:
                empty_subject_obj = Subject.objects.get(name='-')
            except:
                empty_subject_obj = Subject.objects.create(name='-')
            studclass_serialized.save()
            studclass_obj = StudClass.objects.get(stud_class_name=studclass_serialized.data['stud_class_name'])
            if request.data['is_lab'] == 'false':
                studclass_obj.is_lab = False
            elif request.data['is_lab'] == 'true':
                studclass_obj.is_lab = True
            studclass_obj.save()


            timetable_obj = TimeTable.objects.create(stud_class_name = studclass_obj)
            empty_subject_id = empty_subject_obj.pk
            for i in range(5):
                timetable_obj.monday = [empty_subject_id for i in range(5)]
                timetable_obj.tuesday = [empty_subject_id for i in range(5)]
                timetable_obj.wednesday = [empty_subject_id for i in range(5)]
                timetable_obj.thursday = [empty_subject_id for i in range(5)]
                timetable_obj.friday = [empty_subject_id for i in range(5)]
            timetable_obj.save()

            return Response(studclass_serialized.data,status=status.HTTP_201_CREATED)
        print(studclass_serialized)

        return Response(studclass_serialized.errors,status=status.HTTP_400_BAD_REQUEST)

#view to show teacher names in classes section        
class TeacherRetrieveView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def get(self, request, *args, **kwargs):
        teacherFields = TeacherUser.objects.all()
        studClasses = StudClass.objects.all()
        teacher_serialized = TeacherRetrieveSerializer(teacherFields,many=True)
        #Make a copy of teacher_serialized data
        all_teachers = teacher_serialized.data[:]
        for teacher in all_teachers:
            if teacher['is_staff'] == True:
                teacher['stud_class_name'] = 'All'
                continue
            else:
                teacher['stud_class_name'] = ''
            for stud_class in studClasses:
                try:
                    if stud_class.teacher.username == teacher['username']:
                        teacher['stud_class_name'] = stud_class.stud_class_name
                        break
                except:
                    continue
        

        #teacher_objs = TeacherUser.objects.filter
        #stud_class_obj = StudClass.objects.get(teacher = teacher_serialized['id'])
        return Response(all_teachers,status=status.HTTP_200_OK)

#view to retrieve all teachers without any classes assigned for managing studclass
class StudClassRetrieveTeachersView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def get(self,request, *args, **kwargs):
        #retrieve all teachers except administrators
        teacherFields = TeacherUser.objects.filter(is_staff=False)
        studClasses = StudClass.objects.all()
        teacher_serialized = TeacherRetrieveSerializer(teacherFields,many=True)
        #Store ids of teacher with classes assigned
        teacher_ids_with_class = []
        #to store ids of teachers without any classes assigned
        teachers_datas = []
        all_teachers = teacher_serialized.data[:]
        for studClass in studClasses:
            if studClass.teacher:
                teacher_ids_with_class.append(studClass.teacher.id)
        for teacher in teacherFields:
            if teacher.id not in teacher_ids_with_class:
                current_teacher_obj = TeacherUser.objects.get(id=teacher.id)
                teacher_id = current_teacher_obj.id
                teacher_name = current_teacher_obj.name
                current_teacher_data = {'teacher':teacher_id,'teacher_name':teacher_name}
                teachers_datas.append(current_teacher_data)

        print(teacher_ids_with_class)
        print(teachers_datas)
        return Response(teachers_datas,status=status.HTTP_200_OK)

    #view to retrive studclasses that are labs 
class LabStudClassRetrieveView(APIView):
    def get(self,request):
        lab_objs = StudClass.objects.filter(is_lab = True)
        labs_serialized = LabStudClassRetrieveSerializer(lab_objs,many=True)
        print(labs_serialized.data)
        return Response(labs_serialized.data,status=status.HTTP_200_OK)
        
    
# view to retrieve subjects of a specific class or all subjects in all classes
class StudClassSubjectsRetrieveView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        stud_class_name = request.data['stud_class_name']
        subjects_of_studclass = Subject.objects.filter(stud_class_name=stud_class_name)
        subjects_serialized = ClassSubjectsSerializer(subjects_of_studclass, many=True)
        return Response(subjects_serialized.data, status=status.HTTP_200_OK)
    
    def get(self,request):
        subjects = Subject.objects.all()
        subjects_serialized = ClassSubjectsSerializer(subjects, many=True)
        return Response(subjects_serialized.data,status=status.HTTP_200_OK)
    
class StudClassSubjectsCreateView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        subject_serialized = ClassSubjectsCreateSerializer(data=request.data)
        print(request.data)
        if subject_serialized.is_valid():
            subject_serialized.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(subject_serialized.errors, status=status.HTTP_400_BAD_REQUEST)

class StudClassSubjectsEditView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        subject_obj = Subject.objects.get(id=request.data['id'])
        subject_obj.name = request.data['name']
        if request.data['is_lab']=='false':
            subject_obj.is_lab = False
        elif request.data['is_lab']=='true':
            subject_obj.is_lab = True
            
        print(request.data)
        # some subjects might not contain a stud_class_name or lab_name, so objects.get() might crash
        if request.data['stud_class_name'] == '' or request.data['stud_class_name'] == 'null':
            subject_obj.stud_class_name = None
        else:
            stud_class_obj = StudClass.objects.get(stud_class_name = request.data['stud_class_name'])
            subject_obj.stud_class_name = stud_class_obj

        
        if request.data['lab_name'] == '' or request.data['lab_name'] == 'null' or subject_obj.is_lab==False:
            subject_obj.lab_name = None
        else:
            lab_obj = StudClass.objects.get(stud_class_name = request.data['lab_name'])
            subject_obj.lab_name = lab_obj
        subject_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED)  

class TimeTableRetrieveView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        stud_class_name = request.data['stud_class_name']
        stud_class_obj = StudClass.objects.get(stud_class_name=stud_class_name)
        timetable_obj = TimeTable.objects.get(stud_class_name=stud_class_obj)
        class_timetable = {'Monday':{},'Tuesday':{},'Wednesday':{},'Thursday':{},'Friday':{}}
        timetable_subnames = {'Monday':[],'Tuesday':[],'Wednesday':[],'Thursday':[],'Friday':[]}
        timetable_subnames['Monday'] = [Subject.objects.get(id=timetable_obj.monday[i]).name for i in range(5)]
        timetable_subnames['Tuesday'] = [Subject.objects.get(id=timetable_obj.tuesday[i]).name for i in range(5)]
        timetable_subnames['Wednesday'] = [Subject.objects.get(id=timetable_obj.wednesday[i]).name for i in range(5)]
        timetable_subnames['Thursday'] = [Subject.objects.get(id=timetable_obj.thursday[i]).name for i in range(5)]
        timetable_subnames['Friday'] = [Subject.objects.get(id=timetable_obj.friday[i]).name for i in range(5)]


        for i in range(5):
            class_timetable['Monday'][i] = timetable_obj.monday[i]
            class_timetable['Tuesday'][i] = timetable_obj.tuesday[i]
            class_timetable['Wednesday'][i] = timetable_obj.wednesday[i]
            class_timetable['Thursday'][i] = timetable_obj.thursday[i]
            class_timetable['Friday'][i] = timetable_obj.friday[i]
        print(class_timetable)
        timetable_and_subject_names = [class_timetable,timetable_subnames]
        return Response(timetable_and_subject_names,status=status.HTTP_200_OK)
    
class TimeTableRetrieveSubjectNames(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        timetable = ujson.loads(request.data['timetable'])   
        timetable_subnames = {'Monday':[],'Tuesday':[],'Wednesday':[],'Thursday':[],'Friday':[]}
        for day in timetable.keys():
            timetable_subnames[day] = [Subject.objects.get(id=int(value)).name for value in timetable[day].values()]
        print("subname are: ",timetable_subnames)
        return Response(timetable_subnames,status=status.HTTP_200_OK)


class StudClassManageView(APIView):
    parser_classes = [MultiPartParser,FormParser]

    def post(self,request):
        stud_class_name = request.data['stud_class_name']
        new_timetable = ujson.loads(request.data['new_timetable'])
        print(request.data)
        stud_class_obj = StudClass.objects.get(stud_class_name=stud_class_name)

        if request.data['is_lab']=='false':
            stud_class_obj.is_lab = False
        elif request.data['is_lab']=='true':
            stud_class_obj.is_lab = True 

        if request.data['teacher_id']!='' and request.data['teacher_id']!='null':
            teacher_obj = TeacherUser.objects.get(id=int(request.data['teacher_id']))
            print("if part worked")
            stud_class_obj.teacher = teacher_obj
            stud_class_obj.save()
        else:
            stud_class_obj.teacher = None
            stud_class_obj.save()
        
        timetable_obj = TimeTable.objects.get(stud_class_name=stud_class_obj)



        monday_subs = []
        for index in new_timetable['Monday'].keys():
            monday_subs.append(new_timetable['Monday'][index])
            cur_subj_obj = Subject.objects.get(id=new_timetable['Monday'][index])
            if(cur_subj_obj.is_lab):
                lab_obj = StudClass.objects.get(stud_class_name=cur_subj_obj.lab_name.stud_class_name)
                lab_timetable_obj = TimeTable.objects.get(stud_class_name=lab_obj)
                new_lab_subs = lab_timetable_obj.monday
                new_lab_subs[int(index)] = new_timetable['Monday'][index]
                lab_timetable_obj.monday = new_lab_subs
                lab_timetable_obj.save()
        timetable_obj.monday = monday_subs
            
        tuesday_subs = []
        for index in new_timetable['Tuesday'].keys():
            tuesday_subs.append(new_timetable['Tuesday'][index])
            cur_subj_obj = Subject.objects.get(id=new_timetable['Tuesday'][index])
            if(cur_subj_obj.is_lab):
                lab_obj = StudClass.objects.get(stud_class_name=cur_subj_obj.lab_name.stud_class_name)
                lab_timetable_obj = TimeTable.objects.get(stud_class_name=lab_obj)
                new_lab_subs = lab_timetable_obj.tuesday
                new_lab_subs[int(index)] = new_timetable['Tuesday'][index]
                lab_timetable_obj.tuesday = new_lab_subs
                lab_timetable_obj.save()
        timetable_obj.tuesday = tuesday_subs
        
        wednesday_subs = []
        for index in new_timetable['Wednesday'].keys():
            wednesday_subs.append(new_timetable['Wednesday'][index])
            cur_subj_obj = Subject.objects.get(id=new_timetable['Wednesday'][index])
            if(cur_subj_obj.is_lab):
                lab_obj = StudClass.objects.get(stud_class_name=cur_subj_obj.lab_name.stud_class_name)
                lab_timetable_obj = TimeTable.objects.get(stud_class_name=lab_obj)
                new_lab_subs = lab_timetable_obj.wednesday
                new_lab_subs[int(index)] = new_timetable['Wednesday'][index]
                lab_timetable_obj.wednesday = new_lab_subs
                lab_timetable_obj.save()
        timetable_obj.wednesday = wednesday_subs

        thursday_subs = []
        for index in new_timetable['Thursday'].keys():
            thursday_subs.append(new_timetable['Thursday'][index])
            cur_subj_obj = Subject.objects.get(id=new_timetable['Thursday'][index])
            if(cur_subj_obj.is_lab):
                lab_obj = StudClass.objects.get(stud_class_name=cur_subj_obj.lab_name.stud_class_name)
                lab_timetable_obj = TimeTable.objects.get(stud_class_name=lab_obj)
                new_lab_subs = lab_timetable_obj.thursday
                new_lab_subs[int(index)] = new_timetable['Thursday'][index]
                lab_timetable_obj.thursday = new_lab_subs
                lab_timetable_obj.save()
        timetable_obj.thursday = thursday_subs

        friday_subs = []
        for index in new_timetable['Friday'].keys():
            friday_subs.append(new_timetable['Friday'][index])
            cur_subj_obj = Subject.objects.get(id=new_timetable['Friday'][index])
            if(cur_subj_obj.is_lab):
                lab_obj = StudClass.objects.get(stud_class_name=cur_subj_obj.lab_name.stud_class_name)
                lab_timetable_obj = TimeTable.objects.get(stud_class_name=lab_obj)
                new_lab_subs = lab_timetable_obj.friday
                new_lab_subs[int(index)] = new_timetable['Friday'][index]
                lab_timetable_obj.friday = new_lab_subs
                lab_timetable_obj.save()
        timetable_obj.friday = friday_subs
        
        
        # stud_class_obj.stud_class_name = request.data['stud_class_name']



        # timetable_obj.monday = [new_timetable['Monday'][index] for index in new_timetable['Monday'].keys()]
        # timetable_obj.tuesday = [new_timetable['Tuesday'][index] for index in new_timetable['Tuesday'].keys()]
        # timetable_obj.wednesday = [new_timetable['Wednesday'][index] for index in new_timetable['Wednesday'].keys()]
        # timetable_obj.thursday = [new_timetable['Thursday'][index] for index in new_timetable['Thursday'].keys()]
        # timetable_obj.friday = [new_timetable['Friday'][index] for index in new_timetable['Friday'].keys()]


        print(timetable_obj)
        timetable_obj.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class CheckImageForFaceView(APIView):
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        face_photo_b64 = request.data['face_photo_b64']
        valid = face_check.checkIfFacePhotoIsValid(face_photo_b64)
        if(valid):
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DetectFaceView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    parser_classes = [MultiPartParser,FormParser]
    def post(self,request):
        #Convert querydict object to python dict
        #request_as_dict = request.data.dict()
        images_to_detect = ujson.loads(request.data['images_to_detect'])
        #face_photo_b64 = request.data['face_photo_b64']
        stud_class_name = request.data['stud_class_name']
        #stud_class_name = request_as_dict['stud_class_name']
        #convert json string to python list
        #images_to_detect = getImagesToDetectFromRequest(request)
        #print(images_to_detect)
        #images_to_detect = ujson.loads(request_as_dict['captured_images'])
        #print(images_to_detect)
        filename = 'face_data/'+str(stud_class_name) + '.fac'
            #detected_id = face_check.detectFaceFromPickleMultiProcess(filename,images_to_detect)
            #student = Student.objects.get(id=detected_id)
            #detected_name = student.name
        detected_id = face_check.predictStudentIdFromFace(images_to_detect, stud_class_name)
        if(detected_id==-1):
            student_name = "Unknown"
        else:
            student = Student.objects.get(id=detected_id)
            student_name = student.name
        return Response({'matched_name':student_name},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        #print(detected_name)
        return Response({'matched_name':detected_id},status=status.HTTP_200_OK)

'''       face_to_detect = request.data['face_photo_b64']

        filename = 'face_data/'+str(stud_class_name) + '.fac'
        print(filename)
        try:
            detected_id = face_check.detectFaceFromPickle(filename,face_to_detect)
            print(detected_id)
            json_data = {'detected_id': str(detected_id)}
            return Response(json_data,status=status.HTTP_202_ACCEPTED)
        except:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)'''


        

