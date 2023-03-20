from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenBlacklistView

from .views import TeacherUserCreate,TeacherRetrieveView,ObtainTokenPairWithColorView,TeacherUserCompleteRegistration,TeacherDeleteView,StudentRetrieveView,StudentRetrieveView,RetrieveUserTypeAndStudClassName,RetrieveTeacherUserName,StudClassRetrieve,StudentCreateView,StudentEditView,TeacherEditView,StudentDeleteView,DetectFaceView,CheckImageForFaceView,StudClassOperationsForClassesView,StudClassCreateView,StudClassRetrieveTeachersView,StudClassSubjectsRetrieveView,StudClassSubjectsCreateView,StudClassSubjectsEditView,TimeTableRetrieveView,StudClassManageView,TimeTableRetrieveSubjectNames,LabStudClassRetrieveView,AttendanceMarkingView,AttendanceCurrentSubjectView,AttendanceRetrieveView,AttendancePrintView,AttendancePercentageRetrieve,AttendanceAutoCreateObjectsOnTeacherLoginView,MultipleStudentsUpdateStudClass,AcademicBatchRetrieveView,AttendanceEditView,AcademicBatchCreateView
urlpatterns = [
    path('teacher/create/', TeacherUserCreate.as_view(), name="create_teacher"),

    path('teacher/completeregister/', TeacherUserCompleteRegistration.as_view(), name="complete_register"),

    path('token/obtain/', ObtainTokenPairWithColorView.as_view(), name='token_create'),  # override sjwt stock token

    path('token/blacklist/', TokenBlacklistView.as_view(), name="blacklist_token"),

    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    #path('hello/', HelloWorldView.as_view(), name='hello_world'),

    path('teacher/edit/', TeacherEditView.as_view(),name="edit_teacher"),

    path('teacher/retrieve/',TeacherRetrieveView.as_view(), name='teacher_retrieve',),

    path('teacher/delete/',TeacherDeleteView.as_view(), name='teacher_delete',),

    path('studclass/retrieve/',StudClassRetrieve.as_view(), name='stud_class_operations'),

    path('studclass/lab/retrieve/',LabStudClassRetrieveView.as_view(),name = 'lab_retrieve'),

    path('studclassforclasses/retrieve/',StudClassOperationsForClassesView.as_view(), name='stud_class_for_classes_operations'),

    path('studclass/create/',StudClassCreateView.as_view(),name="studclass_create"),

    path('studclass/manage/teacher/retrieve',StudClassRetrieveTeachersView.as_view(), name="retrieve_teachers_without_class"),

    path('student/retrieve/',StudentRetrieveView.as_view(), name='student_retrieve'),

    #path('student/retrieve/classname', StudentRetrieveView.as_view(), name='student_retrieve_by_class_name'),
    
    #path('studclass/retrieve/classname/', StudClassRetrieveClassNameView.as_view(),name='stud_class_name_retrieve'),

    path('usertypestudclass/retrieve/',RetrieveUserTypeAndStudClassName.as_view(), name="retrieve_user_type_and_stud_class_name"),

    path('student/create/', StudentCreateView.as_view(),name="create_student"),

    path('student/edit/', StudentEditView.as_view(),name="edit_student"),

    path('students/update/studclasses/',MultipleStudentsUpdateStudClass.as_view(),name='update_multiple_student_classes'),

    path('student/delete/',StudentDeleteView.as_view(),name="delete_student"),

    path('teacher/retrieve/username/', RetrieveTeacherUserName.as_view(), name="retrieve_user_type_and_stud_class_name"),
    
    path('detect/face/',DetectFaceView.as_view(),name="edit_student"),

    path('face_photo/check_valid/',CheckImageForFaceView.as_view(), name="check_image_for_face"),

    path('classsubjects/retrieve/',StudClassSubjectsRetrieveView.as_view(), name="get_stud_class_subjects"),

    path('classsubject/create/',StudClassSubjectsCreateView.as_view(), name="create_subject"),

    path('classsubject/edit/',StudClassSubjectsEditView.as_view(),name='edit_subject'),

    path('timetable/retrieve/',TimeTableRetrieveView.as_view(),name="retrieve_timetable"),

    path('timetable/retrieve/subjectnames/',TimeTableRetrieveSubjectNames.as_view(),name='retrieve_timetable_with_subject_names'),

    path('studclass/manage/',StudClassManageView.as_view(),name="manage_studclass"),

    path('attendance/marking/',AttendanceMarkingView.as_view(),name='mark_attendance'),

    path('attendance/currentsubject/',AttendanceCurrentSubjectView.as_view(),name='attendance_find_current_subject'),

    path('attendance/retrieve/',AttendanceRetrieveView.as_view(),name='attendance_retreve_all'),

    path('attendance/print/',AttendancePrintView.as_view(),name='attendance_print'),

    path('attendance/retrieve/percentage/',AttendancePercentageRetrieve.as_view(),name='attendance_percentage'),

    path('attendance/onteacherlogin/create/',AttendanceAutoCreateObjectsOnTeacherLoginView.as_view(),name='attendance_autocreate'),

    path('academicbatch/retrieve/',AcademicBatchRetrieveView.as_view(),name='retrieve_batches'),

    path('academicbatch/create/',AcademicBatchCreateView.as_view(),name='create_batch'),

    path('attendance/edit/',AttendanceEditView.as_view(),name='edit_attendance'),
    #'path('teacher/edit/',TeacherEditView.as_view(), name="teacher_edit"),
]
 