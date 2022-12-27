from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import TeacherUserCreate,TeacherRetrieveView,ObtainTokenPairWithColorView,TeacherUserCompleteRegistration,BlackListRefreshView,TeacherDeleteView,StudentRetrieveView,StudentRetrieveView,RetrieveUserTypeAndStudClassName,RetrieveTeacherUserName,StudClassRetrieve,StudentCreateView,StudentEditView,TeacherEditView,StudentDeleteView
urlpatterns = [
    path('teacher/create/', TeacherUserCreate.as_view(), name="create_teacher"),

    path('teacher/completeregister/', TeacherUserCompleteRegistration.as_view(), name="complete_register"),

    path('token/obtain/', ObtainTokenPairWithColorView.as_view(), name='token_create'),  # override sjwt stock token

    path('token/blacklist/', BlackListRefreshView.as_view(), name="blacklist_token"),

    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    #path('hello/', HelloWorldView.as_view(), name='hello_world'),

    path('teacher/edit/', TeacherEditView.as_view(),name="edit_teacher"),


    path('teacher/retrieve/',TeacherRetrieveView.as_view(), name='teacher_retrieve',),

    path('teacher/delete/',TeacherDeleteView.as_view(), name='teacher_delete',),

    path('studclass/retrieve/',StudClassRetrieve.as_view(), name='stud_class_operations'),

    path('student/retrieve/',StudentRetrieveView.as_view(), name='student_retrieve'),

    #path('student/retrieve/classname', StudentRetrieveView.as_view(), name='student_retrieve_by_class_name'),
    
    #path('studclass/retrieve/classname/', StudClassRetrieveClassNameView.as_view(),name='stud_class_name_retrieve'),

    path('usertypestudclass/retrieve/',RetrieveUserTypeAndStudClassName.as_view(), name="retrieve_user_type_and_stud_class_name"),

    path('student/create/', StudentCreateView.as_view(),name="create_student"),

    path('student/edit/', StudentEditView.as_view(),name="edit_student"),

    path('student/delete/',StudentDeleteView.as_view(),name="delete_student"),

    path('teacher/retrieve/username/', RetrieveTeacherUserName.as_view(), name="retrieve_user_type_and_stud_class_name")
    #'path('teacher/edit/',TeacherEditView.as_view(), name="teacher_edit"),
]
