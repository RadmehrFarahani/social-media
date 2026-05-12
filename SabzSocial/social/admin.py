from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
# Register your models here.

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display=['username','first_name','last_name','phone']
    list_editable=['phone']
    fieldsets=UserAdmin.fieldsets+(
        ('Additional Information',{'fields':('date_of_birth','bio','photo','job')}),
    )

def make_deactivation(modeladmin,request,queryset):
    result=queryset.update(active=False)
    modeladmin.message_user(request,{f"{result} Post rejected "})
make_deactivation.short_description='DeActive'
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [ 'author','created','description']
    ordering = ['author', 'created']
    search_fields = ['description']
    actions = [make_deactivation]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['user_from','user_to']

