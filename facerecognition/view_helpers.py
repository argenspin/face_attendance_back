from django.core.mail import send_mail
import threading
import jwt
from .models import StudClass,TeacherUser

#function to identify type of user from jwt token
def identifyUserType(request):
    access_token = request.META['HTTP_AUTHORIZATION'][4:]
    token_decoded = jwt.decode(access_token,'secret',algorithms=['HS256'],options={'verify_signature': False,})
    return token_decoded['user_type']

def identifyTeacherStudClass(request):
    access_token = request.META['HTTP_AUTHORIZATION'][4:]
    token_decoded = jwt.decode(access_token,'secret',algorithms=['HS256'],options={'verify_signature': False,})
    try:
        teacher_obj = TeacherUser.objects.get(id=token_decoded['user_id'])
        if(teacher_obj.is_staff):
            return 'all'
        stud_class = StudClass.objects.get(teacher=teacher_obj)
        teacher_stud_class_name = stud_class.stud_class_name
        return teacher_stud_class_name
    except:
        return 'Not Assigned'

def identifyTeacherUserId(request):
    access_token = request.META['HTTP_AUTHORIZATION'][4:]
    token_decoded = jwt.decode(access_token,'secret',algorithms=['HS256'],options={'verify_signature': False,})
    return token_decoded['user_id']

def register_completion_mail_send(mail_subject,teacher_email):
    send_mail(
        subject='Teacher Login Details',
        message=mail_subject,
        from_email='',
        recipient_list=[teacher_email],
        fail_silently=False,
    )