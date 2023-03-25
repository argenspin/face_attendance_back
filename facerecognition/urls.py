from django.urls import path,include
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView

from . import views
urlpatterns = [
    path('teacher/create/', views.TeacherUserCreate.as_view(), name="create_teacher"),

    path('teacher/completeregister/', views.TeacherUserCompleteRegistration.as_view(), name="complete_register"),

    path('token/obtain/', views.ObtainTokenPairWithColorView.as_view(), name='token_create'),  # override simplejwt stock token

    path('token/blacklist/', TokenBlacklistView.as_view(), name="blacklist_token"),

    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('teacher/edit/', views.TeacherEditView.as_view(),name="edit_teacher"),

    path('teacher/retrieve/',views.TeacherRetrieveView.as_view(), name='teacher_retrieve',),

    path('teacher/delete/',views.TeacherDeleteView.as_view(), name='teacher_delete',),

    path('studclass/retrieve/',views.StudClassRetrieve.as_view(), name='stud_class_operations'),

    path('studclass/lab/retrieve/',views.LabStudClassRetrieveView.as_view(),name = 'lab_retrieve'),

    path('studclassforclasses/retrieve/',views.StudClassOperationsForClassesView.as_view(), name='stud_class_for_classes_operations'),

    path('studclass/create/',views.StudClassCreateView.as_view(),name="studclass_create"),

    path('studclass/manage/teacher/retrieve',views.StudClassRetrieveTeachersView.as_view(), name="retrieve_teachers_without_class"),

    path('student/retrieve/',views.StudentRetrieveView.as_view(), name='student_retrieve'),

    path('usertypestudclass/retrieve/',views.RetrieveUserTypeAndStudClassName.as_view(), name="retrieve_user_type_and_stud_class_name"),

    path('student/create/', views.StudentCreateView.as_view(),name="create_student"),

    path('student/edit/', views.StudentEditView.as_view(),name="edit_student"),

    path('students/update/studclasses/',views.MultipleStudentsUpdateStudClass.as_view(),name='update_multiple_student_classes'),

    path('student/delete/',views.StudentDeleteView.as_view(),name="delete_student"),

    path('teacher/retrieve/username/', views.RetrieveTeacherUserName.as_view(), name="retrieve_user_type_and_stud_class_name"),
    
    path('detect/face/',views.DetectFaceView.as_view(),name="edit_student"),

    path('face_photo/check_valid/',views.CheckImageForFaceView.as_view(), name="check_image_for_face"),

    path('classsubjects/retrieve/',views.StudClassSubjectsRetrieveView.as_view(), name="get_stud_class_subjects"),

    path('classsubject/create/',views.StudClassSubjectsCreateView.as_view(), name="create_subject"),

    path('classsubject/edit/',views.StudClassSubjectsEditView.as_view(),name='edit_subject'),

    path('timetable/retrieve/',views.TimeTableRetrieveView.as_view(),name="retrieve_timetable"),

    path('timetable/retrieve/subjectnames/',views.TimeTableRetrieveSubjectNames.as_view(),name='retrieve_timetable_with_subject_names'),

    path('studclass/manage/',views.StudClassManageView.as_view(),name="manage_studclass"),

    path('attendance/marking/',views.AttendanceMarkingView.as_view(),name='mark_attendance'),

    path('attendance/currentsubject/',views.AttendanceCurrentSubjectView.as_view(),name='attendance_find_current_subject'),

    path('attendance/retrieve/',views.AttendanceRetrieveView.as_view(),name='attendance_retreve_all'),

    path('attendance/print/',views.AttendancePrintView.as_view(),name='attendance_print'),

    path('attendance/retrieve/percentage/',views.AttendancePercentageRetrieve.as_view(),name='attendance_percentage'),

    path('attendance/onteacherlogin/create/',views.AttendanceAutoCreateObjectsOnTeacherLoginView.as_view(),name='attendance_autocreate'),

    path('academicbatch/retrieve/',views.AcademicBatchRetrieveView.as_view(),name='retrieve_batches'),

    path('academicbatch/create/',views.AcademicBatchCreateView.as_view(),name='create_batch'),

    path('attendance/edit/',views.AttendanceEditView.as_view(),name='edit_attendance'),
]
 