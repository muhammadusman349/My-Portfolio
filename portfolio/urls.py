from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.home, name='home'),

    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/skill/<str:skill_slug>/', views.projects_by_skill, name='projects_by_skill'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/comments/add/', views.add_comment, name='add_comment'),
    path('projects/comments/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('projects/comments/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('projects/comments/<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('projects/comment/<int:pk>/', views.get_comment_html, name='get_comment_html'),

    # Skills URLs
    path('skills/', views.skill_list, name='skill_list'),

    # Education URLs
    path('education/', views.education_list, name='education_list'),

    # Experience URLs
    path('experience/', views.experience_list, name='experience_list'),

    # Contact URLs
    path('contact/', views.contact_view, name='contact'),
    path('contact/list/', views.contact_list, name='contact_list'),
]
