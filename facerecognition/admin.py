from django.contrib import admin
from .models import Student,TeacherUser,StudClass
# Register your models here.

class TeacherUserAdmin(admin.ModelAdmin):
    model = TeacherUser

admin.site.register(TeacherUser, TeacherUserAdmin)
admin.site.register(Student,TeacherUserAdmin)
#admin.site.register(Teacher,TeacherUserAdmin)
admin.site.register(StudClass,TeacherUserAdmin)