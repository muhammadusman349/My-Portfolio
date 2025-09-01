from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import Q
from django.contrib.auth import get_user_model
from portfolio.models import (
    Project, Skill,
    Education, Experience,
    Contact, ProjectComment, ProjectImage, Resume
    )
from portfolio.forms import (
    ProjectForm, SkillForm,
    EducationForm, ExperienceForm,
    ContactResponseForm, CommentResponseForm, ResumeForm
    )


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
            # Save the form without many-to-many fields first
            project = form.save(commit=False)
            project.save()

            # Handle many-to-many fields manually
            project.skills.set(form.cleaned_data['skills'])

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
            education = form.save(commit=False)
            education.user = request.user
            education.save()
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
            'education_to_delete': education_to_delete,
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
        'experience_list': page_obj,
        'sort': sort,
        'is_dashboard': True,
    }

    return render(request, 'dashboard/experience/list.html', context)


@login_required
def experience_create(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user = request.user
            experience.save()
            # Save ManyToMany fields like technologies_used and related_projects
            form.save_m2m()
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
            # Save the form without many-to-many fields first
            experience = form.save(commit=False)
            experience.save()

            # Handle many-to-many fields manually
            experience.technologies_used.set(form.cleaned_data['technologies_used'])
            experience.related_projects.set(form.cleaned_data['related_projects'])

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

        try:
            # Convert string IDs to integers
            experience_ids = [int(id) for id in experience_ids if id.isdigit()]
            experience_to_delete = Experience.objects.filter(id__in=experience_ids)
            
            # Check if we have any valid experiences to delete
            if not experience_to_delete.exists():
                messages.error(request, 'No valid experience items found for deletion.')
                return redirect('dashboard:dashboard_experience_list')

            # If confirm=yes is in the POST data, delete the experiences
            if request.POST.get('confirm') == 'yes':
                count = experience_to_delete.count()
                experience_to_delete.delete()
                messages.success(request, f'Successfully deleted {count} experience item(s).')
                return redirect('dashboard:dashboard_experience_list')

            # Show confirmation page with the experiences to be deleted
            context = {
                'experience_items': experience_to_delete,
                'is_dashboard': True,
            }
            return render(request, 'dashboard/experience/delete_multiple.html', context)
            
        except Exception as e:
            messages.error(request, f'An error occurred while deleting experience items: {str(e)}')
            return redirect('dashboard:dashboard_experience_list')
    
    # If not a POST request, redirect to the experience list
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
    # Mark contact as read when viewed
    if not contact.is_read:
        contact.is_read = True
        contact.save()
    if request.method == 'POST':
        form = ContactResponseForm(request.POST)
        if form.is_valid():
            response = form.cleaned_data['response']
            contact.response = response
            contact.responded_at = timezone.now()

            # Prepare email content (HTML + text)
            email_subject = f'Re: {contact.subject}'
            context = {
                'contact': contact,
                'response': response,
                'responder_name': request.user.get_full_name() or request.user.username,
                'responder_email': request.user.email,
                'site_url': request.build_absolute_uri('/').rstrip('/'),
            }

            html_body = render_to_string('emails/contact_response.html', context)
            text_body = strip_tags(html_body)

            # Send email response
            try:
                email = EmailMultiAlternatives(
                    subject=email_subject,
                    body=text_body,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[contact.email],
                    reply_to=[request.user.email] if request.user.email else None,
                )
                email.attach_alternative(html_body, "text/html")
                email.send(fail_silently=False)

                # Save the response only after email is sent successfully
                contact.save()

                # Send confirmation email to admin (plain text is fine)
                admin_confirmation = (
                    f"Response sent to {contact.name} ({contact.email})\n\n"
                    f"Original Message:\nSubject: {contact.subject}\n"
                    f"Sent: {contact.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"Your Response:\n{response}"
                )
                if request.user.email:
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
    
    # Mark comment as read when viewed
    if not comment.is_read:
        comment.is_read = True
        comment.save()
        
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
def user_detail(request, user_id):
    """View detailed information about a specific user."""
    user = get_object_or_404(User, id=user_id)
    
    # Get additional user statistics
    projects_count = user.project_set.count()
    comments_count = user.projectcomment_set.count()
    education_count = user.education_set.count()
    experience_count = user.experience_set.count()
    skills_count = user.skill_set.count()
    contact_messages_count = Contact.objects.filter(email=user.email).count()  # Add total count
    
    # Get recent activity
    recent_projects = user.project_set.order_by('-created_at')[:5]
    recent_comments = user.projectcomment_set.order_by('-created_at')[:5]
    contact_messages = Contact.objects.filter(email=user.email).order_by('-created_at')[:5]
    
    context = {
        'user_detail': user,
        'projects_count': projects_count,
        'comments_count': comments_count,
        'education_count': education_count,
        'experience_count': experience_count,
        'skills_count': skills_count,
        'contact_messages_count': contact_messages_count,  # Add to context
        'recent_projects': recent_projects,
        'recent_comments': recent_comments,
        'contact_messages': contact_messages,
        'is_dashboard': True,
    }
    
    return render(request, 'dashboard/users/detail.html', context)


@login_required
@require_POST
def toggle_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.is_superuser:
            messages.error(request, 'Cannot modify superuser status')
            return redirect('dashboard:dashboard_users_list')

        user.is_active = not user.is_active
        user.save()

        action = "unblocked" if user.is_active else "blocked"
        messages.success(request, f'User {user.username} has been {action} successfully.')

        return redirect('dashboard:dashboard_users_list')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('dashboard:dashboard_users_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('dashboard:dashboard_users_list')


@login_required
@require_POST
def user_delete(request, user_id):
    try:
        user = User.objects.get(id=user_id)

        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser account')
            return redirect('dashboard:dashboard_users_list')

        username = user.username
        user.delete()

        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('dashboard:dashboard_users_list')
        
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('dashboard:dashboard_users_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('dashboard:dashboard_users_list')


@login_required
def user_delete_multiple(request):
    if request.method == 'POST':
        try:
            user_ids = request.POST.getlist('user_ids')
            if not user_ids:
                messages.error(request, 'No users selected for deletion.')
                return redirect('dashboard:dashboard_users_list')

            users_to_delete = User.objects.filter(id__in=user_ids).exclude(is_superuser=True)
            
            # If confirm=yes is in POST, delete the users
            if request.POST.get('confirm') == 'yes':
                count = users_to_delete.count()
                users_to_delete.delete()
                messages.success(request, f'Successfully deleted {count} user(s).')
                return redirect('dashboard:dashboard_users_list')
            
            messages.error(request, 'Invalid request.')
            return redirect('dashboard:dashboard_users_list')
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your request: {str(e)}')
            return redirect('dashboard:dashboard_users_list')
    
    # Handle GET request for confirmation page
    user_ids = request.GET.getlist('user_ids')
    if not user_ids:
        messages.error(request, 'No users selected for deletion.')
        return redirect('dashboard:dashboard_users_list')

    users_to_delete = User.objects.filter(id__in=user_ids).exclude(is_superuser=True)
    if not users_to_delete.exists():
        messages.error(request, 'Selected users not found.')
        return redirect('dashboard:dashboard_users_list')

    context = {
        'users_to_delete': users_to_delete,
        'is_dashboard': True,
    }
    return render(request, 'dashboard/users/delete_multiple.html', context)


@login_required
def resume_upload(request):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('portfolio:home')

    latest_resume = Resume.objects.first()

    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('dashboard:dashboard_resume')
    else:
        form = ResumeForm()

    return render(request, 'dashboard/resume/form.html', {
        'form': form,
        'latest_resume': latest_resume,
        'is_dashboard': True,
    })

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'dashboard/projects/detail.html', {
        'project': project,
        'is_dashboard': True
    })
