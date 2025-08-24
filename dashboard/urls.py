from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),

    # Projects
    path('projects/', views.project_list, name='dashboard_project_list'),
    path('projects/create/', views.project_create, name='dashboard_project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='dashboard_project_edit'),
    path('projects/<int:pk>/', views.project_detail, name='dashboard_project_detail'),
    path('projects/<int:pk>/delete/', views.project_delete, name='dashboard_project_delete'),
    path('projects/delete-multiple/', views.project_delete_multiple, name='dashboard_project_delete_multiple'),
    path('projects/image/<int:image_id>/delete/', views.project_image_delete, name='project_image_delete'),

    # Skills
    path('skills/', views.skill_list, name='dashboard_skill_list'),
    path('skills/create/', views.skill_create, name='dashboard_skill_create'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='dashboard_skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='dashboard_skill_delete'),
    path('skills/delete/multiple/', views.skill_delete_multiple, name='dashboard_skill_delete_multiple'),

    # Education
    path('education/', views.education_list, name='dashboard_education_list'),
    path('education/create/', views.education_create, name='dashboard_education_create'),
    path('education/<int:pk>/edit/', views.education_edit, name='dashboard_education_edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='dashboard_education_delete'),
    path('education/delete/multiple/', views.education_delete_multiple, name='dashboard_education_delete_multiple'),

    # Experience
    path('experience/', views.experience_list, name='dashboard_experience_list'),
    path('experience/create/', views.experience_create, name='dashboard_experience_create'),
    path('experience/<int:pk>/edit/', views.experience_edit, name='dashboard_experience_edit'),
    path('experience/<int:pk>/delete/', views.experience_delete, name='dashboard_experience_delete'),
    path('experience/delete/multiple/', views.experience_delete_multiple, name='dashboard_experience_delete_multiple'),

    # Contact
    path('contacts/', views.contact_list, name='dashboard_contact_list'),
    path('contacts/<int:pk>/', views.contact_detail, name='dashboard_contact_detail'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='dashboard_contact_delete'),
    path('contacts/delete/multiple/', views.contact_delete_multiple, name='dashboard_contact_delete_multiple'),
    path('contacts/<int:pk>/mark-read/', views.mark_contact_read, name='dashboard_mark_contact_read'),
    path('contacts/<int:pk>/mark-unread/', views.mark_contact_unread, name='dashboard_mark_contact_unread'),

    # Comments
    path('comments/', views.dashboard_comment_list, name='dashboard_comment_list'),
    path('comments/<int:pk>/detail/', views.dashboard_comment_detail, name='dashboard_comment_detail'),
    path('comments/<int:pk>/approve/', views.approve_comment, name='dashboard_comment_approve'),
    path('comments/<int:pk>/reject/', views.reject_comment, name='dashboard_comment_reject'),
    path('comments/<int:pk>/delete/', views.dashboard_comment_delete, name='dashboard_comment_delete'),
    path('comments/delete/multiple/', views.dashboard_comment_delete_multiple, name='dashboard_comment_delete_multiple'),

    # Users
    path('users/', views.user_list, name='dashboard_users_list'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/delete-multiple/', views.user_delete_multiple, name='user_delete_multiple'),

    # Resume
    path('resume/', views.resume_upload, name='dashboard_resume'),
]
