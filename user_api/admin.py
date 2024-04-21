from django.contrib import admin
from .models import User, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserAdmin(BaseUserAdmin):
    readonly_fields = ["date_joined"]
    BaseUserAdmin.list_display += ('is_verified',)
    ordering = ['id']
    # exclude = ['first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets+ (
        (                      
            'Extra Fields', # you can also use None 
            {
                'fields': (
                    'is_verified',
                ),
            },
        ),
    )

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super().get_fieldsets(request, obj)
    #     new = []
    #     for name, fields_dict in fieldsets:
    #         if fields_dict['fields'] == ('first_name', 'last_name', 'email'):
    #             fields_dict['fields'] = ('email',)
    #         new.append((name, fields_dict))
    #     return new

class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__email', 'user__username'] 

admin.site.register(User,UserAdmin)
admin.site.register(Profile, ProfileAdmin)