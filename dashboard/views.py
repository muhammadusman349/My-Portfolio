from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth import get_user_model
from portfolio.models import (
    Project, Skill,
    Education, Experience,
    Contact, ProjectComment, ProjectImage
    )
from portfolio.forms import (
    ProjectForm, SkillForm,
    EducationForm, ExperienceForm,
    ContactResponseForm, CommentResponseForm
    )
import json


User = get_user_model()


# def is_superuser(user):
#     return user.is_superuser


# def is_owner(user):
#     """Check if the user is authenticated and is a superuser (owner)"""
#     return user.is_authenticated and user.is_superuser
#     @user_passes_test(is_owner, login_url='portfolio:home')



@login_required
def dashboard_home(request):
    projects_count = Project.objects.count()
    skills_count = Skill.objects.count()
    education_count = Education.objects.count()
    experience_count = Experience.objects.count()
    unread_contacts = Contact.objects.filter(is_read=False).count()
    unresponded_comments = ProjectComment.objects.filter(parent_comment=None).exclude(replies__isnull=False).count()
    users_count = User.objects.count()

    context = {
        'is_dashboard': True,
        'projects_count': projects_count,
        'skills_count': skills_count,
        'education_count': education_count,
        'experience_count': experience_count,
        'unread_contacts': unread_contacts,
        'unresponded_comments': unresponded_comments,
        'users_count': users_count,
    }
    return render(request, 'dashboard/home.html', context)


# Projects Management
@login_required
def project_list(request):
    projects = Project.objects.all()
    # Apply sorting
    sort = request.GET.get('sort', '-created_at')
    projects = projects.order_by(sort)

    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'projects': page_obj,
        'sort': sort,
        'is_dashboard': True,
    }

    return render(request, 'dashboard/projects/list.html', context)


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships

            # Handle multiple image uploads
            images = request.FILES.getlist('images[]')
            captions = request.POST.getlist('captions[]')
            orders = request.POST.getlist('orders[]')

            for i, image in enumerate(images):
                caption = captions[i] if i < len(captions) else ''
                order = int(orders[i]) if i < len(orders) else 0
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    caption=caption,
                    order=order
                )

            messages.success(request, 'Project created successfully!')
            return redirect('dashboard:dashboard_project_list')
    else:
        form = ProjectForm()

    return render(request, 'dashboard/projects/form.html', {
        'form': form,
        'action': 'Create'
    })


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            # Handle multiple image uploads
            images = request.FILES.getlist('images[]')
            captions = request.POST.getlist('captions[]')
            orders = request.POST.getlist('orders[]')

            for i, image in enumerate(images):
                caption = captions[i] if i < len(captions) else ''
                order = int(orders[i]) if i < len(orders) else 0
                ProjectImage.objects.create(
                    project=project,
                    image=image,
                    caption=caption,
                    order=order
                )

            messages.success(request, 'Project updated successfully!')
            return redirect('dashboard:dashboard_project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'dashboard/projects/form.html', {
        'form': form,
        'project': project,
        'action': 'Update'
    })


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('dashboard:dashboard_project_list')
    return render(request, 'dashboard/projects/delete.html', {'project': project})


@login_required
def project_image_delete(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(ProjectImage, id=image_id, project__user=request.user)
        image.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def project_delete_multiple(request):
    if request.method == 'POST':
        project_ids = request.POST.getlist('project_ids')
        if not project_ids:
            messages.error(request, 'No projects selected for deletion.')
            return redirect('dashboard:dashboard_project_list')

        projects_to_delete = Project.objects.filter(id__in=project_ids)
        if request.POST.get('confirm') == 'yes':
            projects_to_delete.delete()
            messages.success(request, 'Selected projects were successfully deleted.')
            return redirect('dashboard:dashboard_project_list')

        context = {
            'project_items': projects_to_delete,
            'is_dashboard': True,
        }
        return render(request, 'dashboard/projects/delete_multiple.html', context)
    return redirect('dashboard:dashboard_project_list')


# Skills Management
@login_required
def skill_list(request):
    skills = Skill.objects.all()

    # Apply sorting
    sort = request.GET.get('sort', 'name')  # Default sort by name
    if sort.startswith('-'):
        skills = skills.order_by(sort)  # Already prefixed with -
    else:
        skills = skills.order_by(sort)

    # Pagination
    paginator = Paginator(skills, 10)  # Show 10 skills per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'skills': page_obj,
        'sort': sort,
        'is_dashboard': True,
    }
    return render(request, 'dashboard/skills/list.html', context)


@login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, 'Skill created successfully!')
            return redirect('dashboard:dashboard_skill_list')
    else:
        form = SkillForm()
    return render(request, 'dashboard/skills/form.html', {'form': form, 'action': 'Create'})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully!')
            return redirect('dashboard:dashboard_skill_list')
    else:
        form = SkillForm(instance=skill)
    return render(request, 'dashboard/skills/form.html', {'form': form, 'action': 'Edit'})


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted successfully.')
        return redirect('dashboard:dashboard_skill_list')
    return render(request, 'dashboard/skills/delete.html', {'skill': skill})


@login_required
def skill_delete_multiple(request):
    if request.method == 'POST':
        try:
            skill_ids = request.POST.getlist('skill_ids')
            confirm = request.POST.get('confirm')
            if not skill_ids:
                messages.error(request, 'No skills selected for deletion.')
                return redirect('dashboard:dashboard_skill_list')
            skills = Skill.objects.filter(id__in=skill_ids)
            if not skills.exists():
                messages.error(request, 'Selected skills not found.')
                return redirect('dashboard:dashboard_skill_list')
            if confirm == 'yes':
                # Delete the skills
                deleted_count = skills.count()
                skills.delete()
                messages.success(request, f'Successfully deleted {deleted_count} skills')
                return redirect('dashboard:dashboard_skill_list')
            # Show confirmation page
            return render(request, 'dashboard/skills/delete_multiple.html', {
                'skills': skills,
                'skill_ids': skill_ids,
            })
        except Exception as e:
            messages.error(request, f'Error deleting skills: {str(e)}')
    return redirect('dashboard:dashboard_skill_list')


# Education Management
@login_required
def education_list(request):
    education_items = Education.objects.all()
    # Apply sorting
    sort = request.GET.get('sort', '-start_date')
    education_items = education_items.order_by(sort)

    # Pagination
    paginator = Paginator(education_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'education_items': page_obj,
        'sort': sort,
        'is_dashboard': True,
    }
    return render(request, 'dashboard/education/list.html', context)


@login_required
def education_create(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save()
            messages.success(request, 'Education created successfully!')
            return redirect('dashboard:dashboard_education_list')
    else:
        form = EducationForm()
    return render(request, 'dashboard/education/form.html', {'form': form, 'action': 'Create'})


@login_required
def education_edit(request, pk):
    education = get_object_or_404(Education, pk=pk)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education updated successfully!')
            return redirect('dashboard:dashboard_education_list')
    else:
        form = EducationForm(instance=education)
    return render(request, 'dashboard/education/form.html', {'form': form, 'action': 'Edit', 'is_dashboard': True})


@login_required
def education_delete(request, pk):
    education = get_object_or_404(Education, pk=pk)
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education deleted successfully!')
        return redirect('dashboard:dashboard_education_list')
    return render(request, 'dashboard/education/delete.html', {'education': education, 'is_dashboard': True})


@login_required
def education_delete_multiple(request):
    if request.method == 'POST':
        education_ids = request.POST.getlist('education_ids')
        if not education_ids:
            messages.error(request, 'No education items selected for deletion.')
            return redirect('dashboard:dashboard_education_list')

        education_to_delete = Education.objects.filter(id__in=education_ids)
        if request.POST.get('confirm') == 'yes':
            education_to_delete.delete()
            messages.success(request, 'Selected education items were successfully deleted.')
            return redirect('dashboard:dashboard_education_list')

        context = {
            'education_items': education_to_delete,
            'is_dashboard': True,
        }
        return render(request, 'dashboard/education/delete_multiple.html', context)
    return redirect('dashboard:dashboard_education_list')


# Experience Management
@login_required
def experience_list(request):
    experience_items = Experience.objects.all()

    # Apply sorting
    sort = request.GET.get('sort', '-start_date')
    experience_items = experience_items.order_by(sort)

    # Pagination
    paginator = Paginator(experience_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'experience_items': page_obj,
        'sort': sort,
        'is_dashboard': True,
    }

    return render(request, 'dashboard/experience/list.html', context)


@login_required
def experience_create(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save()
            messages.success(request, 'Experience created successfully!')
            return redirect('dashboard:dashboard_experience_list')
    else:
        form = ExperienceForm()
    return render(request, 'dashboard/experience/form.html', {'form': form, 'action': 'Create'})


@login_required
def experience_edit(request, pk):
    experience = get_object_or_404(Experience, pk=pk)
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, 'Experience updated successfully!')
            return redirect('dashboard:dashboard_experience_list')
    else:
        form = ExperienceForm(instance=experience)
    return render(request, 'dashboard/experience/form.html', {'form': form, 'action': 'Edit', 'is_dashboard': True})


@login_required
def experience_delete(request, pk):
    experience = get_object_or_404(Experience, pk=pk)
    if request.method == 'POST':
        experience.delete()
        messages.success(request, 'Experience deleted successfully!')
        return redirect('dashboard:dashboard_experience_list')
    return render(request, 'dashboard/experience/delete.html', {'experience': experience, 'is_dashboard': True})


@login_required
def experience_delete_multiple(request):
    if request.method == 'POST':
        experience_ids = request.POST.getlist('experience_ids')
        if not experience_ids:
            messages.error(request, 'No experience items selected for deletion.')
            return redirect('dashboard:dashboard_experience_list')

        experience_to_delete = Experience.objects.filter(id__in=experience_ids)
        if request.POST.get('confirm') == 'yes':
            experience_to_delete.delete()
            messages.success(request, 'Selected experience items were successfully deleted.')
            return redirect('dashboard:dashboard_experience_list')

        context = {
            'experience_items': experience_to_delete,
            'is_dashboard': True,
        }
        return render(request, 'dashboard/experience/delete_multiple.html', context)
    return redirect('dashboard:dashboard_experience_list')


# Contact Management
@login_required
def contact_list(request):
    sort = request.GET.get('sort', '-created_at')
    contacts = Contact.objects.all()

    if sort == 'name':
        contacts = contacts.order_by('name')
    elif sort == '-name':
        contacts = contacts.order_by('-name')
    elif sort == 'email':
        contacts = contacts.order_by('email')
    elif sort == '-email':
        contacts = contacts.order_by('-email')
    elif sort == 'created_at':
        contacts = contacts.order_by('created_at')
    else:  # Default to newest first
        contacts = contacts.order_by('-created_at')

    paginator = Paginator(contacts, 10)
    page = request.GET.get('page')
    try:
        contact_items = paginator.page(page)
    except PageNotAnInteger:
        contact_items = paginator.page(1)
    except EmptyPage:
        contact_items = paginator.page(paginator.num_pages)

    context = {
        'contact_items': contact_items,
        'sort': sort,
        'is_dashboard': True
    }
    return render(request, 'dashboard/contacts/list.html', context)


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactResponseForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            contact.response = response
            contact.responded_at = timezone.now()

            # Prepare email content
            email_subject = f'Re: {contact.subject}'
            email_body = f"""Dear {contact.name},

Thank you for your message regarding "{contact.subject}".

{response}

Best regards,
{request.user.get_full_name() or request.user.username}"""
 
            # Send email response
            try:
                # First, try sending to contact
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[contact.email],
                    fail_silently=False,
                )
                # Save the response only after email is sent successfully
                contact.save()
                # Send confirmation email to admin
                admin_confirmation = f"""Response sent to {contact.name} ({contact.email})

Original Message:
Subject: {contact.subject}
Sent: {contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Your Response:
{response}"""

                send_mail(
                    subject=f'Confirmation: Response sent to {contact.name}',
                    message=admin_confirmation,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )

                messages.success(request, f'Response sent successfully to {contact.email}!')
                return redirect('dashboard:dashboard_contact_list')
            except Exception as e:
                print(f"Email Error: {str(e)}")
                messages.error(request, f'Failed to send email. Please check your email settings and try again. Error: {str(e)}')
    else:
        form = ContactResponseForm(initial={'response': contact.response})
    return render(request, 'dashboard/contacts/detail.html', {
        'contact': contact,
        'form': form,
        'is_dashboard': True
    })


@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact deleted successfully!')
        return redirect('dashboard:dashboard_contact_list')
    return render(request, 'dashboard/contacts/delete.html', {'contact': contact, 'is_dashboard': True})


@login_required
def contact_delete_multiple(request):
    if request.method == 'POST':
        contact_ids = request.POST.getlist('contact_ids')
        if not contact_ids:
            messages.error(request, 'No contacts selected for deletion.')
            return redirect('dashboard:dashboard_contact_list')

        contacts_to_delete = Contact.objects.filter(id__in=contact_ids)
        if not contacts_to_delete.exists():
            messages.error(request, 'Selected contacts not found.')
            return redirect('dashboard:dashboard_contact_list')

        if request.POST.get('confirm') == 'yes':
            deleted_count = contacts_to_delete.count()
            contacts_to_delete.delete()
            messages.success(request, f'Successfully deleted {deleted_count} contacts.')
            return redirect('dashboard:dashboard_contact_list')

        # Show confirmation page
        return render(request, 'dashboard/contacts/delete_multiple.html', {
            'contacts_to_delete': contacts_to_delete,
            'is_dashboard': True
        })
    return redirect('dashboard:dashboard_contact_list')


# Comment Management
@login_required
def dashboard_comment_list(request):
    sort = request.GET.get('sort', '-created_at')
    comments = ProjectComment.objects.all()

    if sort == 'project':
        comments = comments.order_by('project__title')
    elif sort == '-project':
        comments = comments.order_by('-project__title')
    elif sort == 'name':
        comments = comments.order_by('name')
    elif sort == '-name':
        comments = comments.order_by('-name')
    elif sort == 'created_at':
        comments = comments.order_by('created_at')
    else:  # Default to newest first
        comments = comments.order_by('-created_at')

    paginator = Paginator(comments, 10)
    page = request.GET.get('page')
    try:
        comment_items = paginator.page(page)
    except PageNotAnInteger:
        comment_items = paginator.page(1)
    except EmptyPage:
        comment_items = paginator.page(paginator.num_pages)

    context = {
        'comment_items': comment_items,
        'sort': sort,
        'is_dashboard': True
    }
    return render(request, 'dashboard/comments/list.html', context)


@login_required
def dashboard_comment_detail(request, pk):
    comment = get_object_or_404(ProjectComment, pk=pk)
    replies = comment.get_replies().order_by('created_at')

    if request.method == 'POST':
        form = CommentResponseForm(request.POST)
        if form.is_valid():
            response_text = form.cleaned_data['response']
            # Create a reply
            reply = ProjectComment.objects.create(
                project=comment.project,
                user=request.user,
                text=response_text,
                parent_comment=comment,
                is_owner_reply=True,
                status='approved'  # Auto-approve owner replies
            )
            messages.success(request, 'Reply added successfully!')
            return redirect('dashboard:dashboard_comment_detail', pk=comment.pk)
    else:
        form = CommentResponseForm()

    return render(request, 'dashboard/comments/detail.html', {
        'comment': comment,
        'replies': replies,
        'form': form,
        'is_dashboard': True
    })


@login_required
def dashboard_comment_delete(request, pk):
    comment = get_object_or_404(ProjectComment, pk=pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('dashboard:dashboard_comment_list')
    return render(request, 'dashboard/comments/delete.html', {'comment': comment, 'is_dashboard': True})


@login_required
def dashboard_comment_delete_multiple(request):
    if request.method == 'POST':
        comment_ids = request.POST.getlist('comment_ids')
        if not comment_ids:
            messages.error(request, 'No comments selected for deletion.')
            return redirect('dashboard:dashboard_comment_list')

        comments_to_delete = ProjectComment.objects.filter(id__in=comment_ids)
        if request.POST.get('confirm') == 'yes':
            comments_to_delete.delete()
            messages.success(request, 'Selected comments were successfully deleted.')
            return redirect('dashboard:dashboard_comment_list')

        context = {
            'comment_items': comments_to_delete,
            'is_dashboard': True,
        }
        return render(request, 'dashboard/comments/delete_multiple.html', context)
    return redirect('dashboard:dashboard_comment_list')


@login_required
def approve_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(ProjectComment, pk=pk)
        comment.status = 'approved'
        comment.save()
        messages.success(request, 'Comment approved successfully!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def reject_comment(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(ProjectComment, pk=pk)
        comment.status = 'rejected'
        comment.save()
        messages.success(request, 'Comment rejected successfully!')
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def mark_contact_read(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        contact = get_object_or_404(Contact, pk=pk)
        contact.is_read = True
        contact.save()
        return JsonResponse({'status': 'success'})
    except Contact.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Contact not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def mark_contact_unread(request, pk):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        contact = get_object_or_404(Contact, pk=pk)
        contact.is_read = False
        contact.save()
        return JsonResponse({'status': 'success'})
    except Contact.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Contact not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def user_list(request):
    search_query = request.GET.get('search', '')
    users = User.objects.all()

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    users = users.order_by('-date_joined')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 10)  # Show 10 users per page

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context = {
        'users': users,
        'search_query': search_query,
        'is_dashboard': True,  # Add this line
    }

    return render(request, 'dashboard/users/list.html', context)


@login_required
@require_POST
def toggle_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot modify superuser status'
            }, status=403)

        user.is_active = not user.is_active
        user.save()

        action = "unblocked" if user.is_active else "blocked"
        messages.success(request, f'User {user.username} has been {action} successfully.')

        return JsonResponse({
            'status': 'success',
            'message': f'User has been {action}',
            'is_active': user.is_active
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def user_delete(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete superuser account'
            }, status=403)

        username = user.username
        user.delete()

        messages.success(request, f'User {username} has been deleted successfully.')

        return JsonResponse({
            'status': 'success',
            'message': f'User {username} has been deleted'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def user_delete_multiple(request):
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])

        if not user_ids:
            return JsonResponse({
                'status': 'error',
                'message': 'No users selected'
            }, status=400)

        # Exclude superusers from deletion
        users = User.objects.filter(id__in=user_ids).exclude(is_superuser=True)
        deleted_count = users.count()

        if deleted_count == 0:
            return JsonResponse({
                'status': 'error',
                'message': 'No valid users to delete'
            }, status=400)

        # Store usernames before deletion
        usernames = list(users.values_list('username', flat=True))
        # Delete users
        users.delete()

        if deleted_count == 1:
            messages.success(request, f'User {usernames[0]} has been deleted successfully.')
        else:
            messages.success(request, f'{deleted_count} users have been deleted successfully.')

        return JsonResponse({
            'status': 'success',
            'message': f'{deleted_count} users deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
