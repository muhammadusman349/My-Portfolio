from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'location', 'birth_date')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'location')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('bio', 'profile_picture', 'location', 'birth_date')}),
        ('Social Links', {'fields': ('linkedin', 'github', 'website')}),
    )
