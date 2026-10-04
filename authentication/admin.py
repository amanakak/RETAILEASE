from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# Unregister the default User admin
admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('role', 'phone', 'address')

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'userprofile__role')
    
    def get_role(self, obj):
        try:
            return obj.userprofile.get_role_display()
        except:
            return 'No Profile'
    get_role.short_description = 'Role'

# Register the new User admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)
