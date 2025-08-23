from django.contrib import admin
from .models import (
    Project, ProjectComment,
    Skill, Education,
    Contact, Experience,
    ProjectImage, Resume
    )

# Register your models here.


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectImageInline]
    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'skills__name')
    date_hierarchy = 'created_at'
    filter_horizontal = ('skills',)


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'image', 'caption', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('caption', 'project__title')
    date_hierarchy = 'created_at'

@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'project__title')
    date_hierarchy = 'created_at'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'proficiency')
    list_filter = ('id', 'proficiency')
    search_fields = ('name', 'user__username')
    list_editable = ('proficiency',)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('id','institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'user')
    list_filter = ('start_date', 'end_date')
    search_fields = ('institution', 'degree', 'field_of_study', 'user__username')
    date_hierarchy = 'start_date'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'subject', 'message', 'is_read', 'created_at')
    list_filter = ('name', 'email')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company', 'position', 'employment_type', 'location', 'start_date', 'end_date', 'current', 'description', 'company_url')
    list_filter = ('start_date', 'end_date', 'current')
    search_fields = ('company', 'position', 'user__username')
    date_hierarchy = 'start_date'


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username',)
    date_hierarchy = 'uploaded_at'
