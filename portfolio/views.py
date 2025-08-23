from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Project, ProjectComment, Skill, Education, Experience, Contact, Resume
from django.contrib import messages
from .forms import CommentForm


def project_list(request):
    project_list = Project.objects.all().order_by('-created_at')
    paginator = Paginator(project_list, 6)  # Show 6 projects per page

    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    return render(request, 'portfolio/project_list.html', {'projects': projects})


@login_required
@require_POST
def add_comment(request, pk):
    """Add a new comment or reply to a project."""
    project = get_object_or_404(Project, pk=pk)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # Get the text from POST data
    text = request.POST.get('text', '').strip()
    parent_id = request.POST.get('parent_id')

    if not text:
        if is_ajax:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        messages.error(request, 'Comment text is required')
        return redirect('portfolio:project_detail', pk=pk)

    try:
        # Create the comment
        comment = ProjectComment(
            project=project,
            user=request.user,
            text=text,
            status='approved' if request.user == project.user else 'pending',
            is_owner_reply=request.user == project.user
        )

        # Set parent comment if provided
        if parent_id:
            try:
                parent_comment = ProjectComment.objects.get(id=parent_id)
                if parent_comment.project_id != project.id:
                    raise ValueError("Invalid parent comment")
                comment.parent_comment = parent_comment
            except ProjectComment.DoesNotExist:
                if is_ajax:
                    return JsonResponse({'error': 'Parent comment not found'}, status=400)
                messages.error(request, 'Parent comment not found')
                return redirect('portfolio:project_detail', pk=pk)

        comment.save()

        if is_ajax:
            context = {
                'comment': comment,
                'project': project,
                'user': request.user,
            }
            comment_html = render_to_string(
                'portfolio/includes/comment.html',
                context,
                request=request
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Comment posted successfully' if comment.status == 'approved' else 'Your comment is pending approval',
                'html': comment_html,
                'comment_id': comment.id,
            })

        messages.success(
            request,
            'Comment posted successfully' if comment.status == 'approved' else 'Your comment is pending approval'
        )
        return redirect('portfolio:project_detail', pk=pk)

    except Exception as e:
        if is_ajax:
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Error posting comment: {str(e)}')
        return redirect('portfolio:project_detail', pk=pk)


@login_required
@require_POST
def edit_comment(request, pk):
    """Edit an existing comment."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    comment = get_object_or_404(ProjectComment, pk=pk)

    if request.user != comment.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Comment text is required'}, status=400)

    try:
        comment.text = text
        comment.is_edited = True
        comment.save()

        return JsonResponse({
            'status': 'success',
            'text': comment.text,
            'is_edited': True
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def delete_comment(request, pk):
    """Delete a comment."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    comment = get_object_or_404(ProjectComment, pk=pk)

    if request.user != comment.user and request.user != comment.project.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    try:
        comment.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def toggle_like(request, pk):
    """Toggle like status on a comment."""
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    comment = get_object_or_404(ProjectComment, pk=pk)

    try:
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True

        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': comment.get_like_count()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    comments = project.comments.filter(
        parent_comment=None,  # Only get top-level comments
        status='approved'     # Only show approved comments
    ).select_related('user').prefetch_related('replies')

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.status = 'pending'
            comment.save()
            messages.success(request, 'Your comment has been submitted and is pending approval.')
            return redirect('portfolio:project_detail', pk=pk)
    else:
        form = CommentForm()

    context = {
        'project': project,
        'comments': comments,
        'comment_form': form,
    }
    return render(request, 'portfolio/project_detail.html', context)


def projects_by_skill(request, skill_slug):
    skill_name = skill_slug.replace('-', ' ')
    try:
        # Get all skills with the given name and combine their projects
        skills = Skill.objects.filter(name__iexact=skill_name)
        project_list = Project.objects.filter(skills__in=skills).distinct().order_by('-created_at')
        paginator = Paginator(project_list, 6)  # Show 6 projects per page

        page = request.GET.get('page')
        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)
    except Skill.DoesNotExist:
        projects = Project.objects.none()

    context = {
        'projects': projects,
        'skill_name': skill_name,
    }
    return render(request, 'portfolio/project_list.html', context)


def skill_list(request):
    skills = Skill.objects.all().order_by('-proficiency')
    return render(request, 'portfolio/skill_list.html', {'skills': skills})


def education_list(request):
    educations = Education.objects.all().order_by('-start_date')
    return render(request, 'portfolio/education_list.html', {'educations': educations})


def experience_list(request):
    experiences = Experience.objects.all().order_by('-start_date')
    return render(request, 'portfolio/experience_list.html', {'experiences': experiences})


def experience_detail(request, pk):
    experience = get_object_or_404(Experience, pk=pk)

    # Get related projects by matching the skills used in the experience
    related_projects = Project.objects.filter(
        skills__in=experience.technologies_used.all()
    ).distinct().order_by('-created_at')

    return render(request, 'portfolio/experience_detail.html', {
        'experience': experience,
        'related_projects': related_projects,
    })


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'portfolio/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })

        try:
            contact = Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('portfolio:contact')
        except Exception as e:
            messages.error(request, 'An error occurred while sending your message. Please try again.')
            return render(request, 'portfolio/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })

    return render(request, 'portfolio/contact.html')


@login_required
def contact_list(request):
    contacts = Contact.objects.all().order_by('-created_at')
    return render(request, 'portfolio/contact_list.html', {'contacts': contacts})


@login_required
def reply_to_response(request, comment_id):
    comment = get_object_or_404(ProjectComment, id=comment_id)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        reply_text = request.POST.get('reply')
        if reply_text and comment.response:  # Only allow replies if there's an admin response
            comment.user_reply = reply_text
            comment.user_reply_date = timezone.now()
            comment.save()
            return JsonResponse({
                'status': 'success',
                'reply': reply_text,
                'reply_date': comment.user_reply_date.strftime("%B %d, %Y"),
                'user_initial': request.user.username[0].upper()
            })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def home(request):
    projects = Project.objects.all().order_by('-created_at')[:3]
    experiences = Experience.objects.all().order_by('-start_date')[:3]
    educations = Education.objects.all().order_by('-start_date')
    skills = Skill.objects.all().order_by('-proficiency')[:8]  # Reduced from 10 to 8 skills
    latest_resume = Resume.objects.first()

    return render(request, 'portfolio/home.html', {
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
        'latest_resume': latest_resume,
    })


@login_required
def get_comment_html(request, pk):
    comment = get_object_or_404(ProjectComment, pk=pk)
    comment._request_user = request.user

    html = render_to_string('portfolio/includes/comment.html',
                          {'comment': comment, 'project': comment.project},
                          request=request)

    return JsonResponse({
        'status': 'success',
        'html': html
    })


def privacy_policy(request):
    return render(request, 'portfolio/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'portfolio/terms_of_service.html')


def resume_latest(request):
    latest_resume = Resume.objects.first()
    if latest_resume and latest_resume.file:
        return redirect(latest_resume.file.url)
    messages.error(request, 'Resume is not available yet.')
    return redirect('portfolio:home')
