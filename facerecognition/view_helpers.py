import base64
from django.core.mail import send_mail
import threading
import jwt
from .models import StudClass,TeacherUser
from concurrent.futures import ProcessPoolExecutor
import time
import ujson
import pdfkit

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

def getImagesToDetectFromRequest(request):
    images_to_detect = []
    results = []
    for i in range(0,50):
        current_image_name = 'image_'+str(i)
        image = request.data[current_image_name]
        images_to_detect.append(request.data[current_image_name])

    return images_to_detect

def writeAttendanceDataToHtmlandGetPDF(attendances):
    attendances = ujson.loads(attendances)
    print(len(attendances))
    file = open('attendance_template.html','w+')
    tags = [
        "<!doctype html>\n"
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
            # '<link rel="stylesheet" href="test_table.css"></style>',
        "</head>",
        # css,
        "<body>",
        '<h1 align="center">Attendance Report</h1>',
        '<br/>',
        '<div class="table-wrapper">',
        '<table class="fl-table">',
            '<tr>',
                '<th>SL No.</th>',
                '<th>Date</th>',
                '<th>Student Name</th>',
                '<th>Class</th>',
                '<th>Batch</th>',
                '<th>Period 1</th>',
                '<th>Period 2</th>',
                '<th>Period 3</th>',
                '<th>Period 4</th>',
                '<th>Period 5</th>',
            '</tr>',
            '<div id="table_data">',
            '</div>',
        '</table>',
        '</div>',
        "</body>",
        "</html>",
    ]
    i=tags.index('<div id="table_data">') + 1
    for attendance in attendances:
        sub1_att_style = ['Present','green'] if attendance['subject1_att'] else ['Absent','red']
        sub2_att_style = ['Present','green'] if attendance['subject2_att'] else ['Absent','red']
        sub3_att_style = ['Present','green'] if attendance['subject3_att'] else ['Absent','red']
        sub4_att_style = ['Present','green'] if attendance['subject4_att'] else ['Absent','red']
        sub5_att_style = ['Present','green'] if attendance['subject5_att'] else ['Absent','red']

        to_insert = ''.join((
        "<tr>",
        '\n<td>',str(attendance['sl_no']), '</td>',
        '\n<td>' , attendance['date'] , '</td>', 
        '\n<td>' , attendance['student_name'] , '</td>' ,
        '\n<td>' , attendance['stud_class_name'] , '</td>',
        '\n<td>' , attendance['batch_name'] , '</td>',
        '\n<td style="color:', sub1_att_style[1],';">' , sub1_att_style[0] , '</td>', 
        '\n<td style="color:', sub2_att_style[1] ,';">', sub2_att_style[0] , '</td>', 
        '\n<td style="color:', sub3_att_style[1] ,';">', sub3_att_style[0] , '</td>', 
        '\n<td style="color:', sub4_att_style[1] ,';">', sub4_att_style[0] , '</td>', 
        '\n<td style="color:', sub5_att_style[1] ,';">', sub5_att_style[0] , '</td>', 
        '\n</tr>', 
        ))        
        
        tags.insert(i,to_insert)
        i+=1
    html_text = '\n'.join(tags)
    file.write(html_text)

    pdfkit.from_string(html_text,'attendance.pdf',css='print_doc_css.css',options={'encoding': "UTF-8"})
    with open('attendance.pdf','rb') as pdf_data:
        b64_pdf = pdf_to_base64(pdf_data)
        return b64_pdf
    
def pdf_to_base64(file):
    file_bytes = base64.b64encode(file.read())
    # base_64 = file_bytes.decode("ascii")
    return file_bytes
    return pdf

