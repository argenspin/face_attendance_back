from django.contrib import admin
from .models import Student,TeacherUser,StudClass,Subject,TimeTable,Attendance,AcademicBatch
# Register your models here.

class TeacherUserAdmin(admin.ModelAdmin):
    model = TeacherUser

admin.site.register(TeacherUser, TeacherUserAdmin)
admin.site.register(Student,TeacherUserAdmin)
#admin.site.register(Teacher,TeacherUserAdmin)
admin.site.register(StudClass,TeacherUserAdmin)
admin.site.register(Subject,TeacherUserAdmin)
admin.site.register(TimeTable,TeacherUserAdmin)
admin.site.register(Attendance,TeacherUserAdmin)
admin.site.register(AcademicBatch,TeacherUserAdmin)
