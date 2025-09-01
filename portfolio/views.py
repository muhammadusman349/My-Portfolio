from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, F, Window, Max
from .models import Project, ProjectComment, Skill, Education, Experience, Contact, Resume
from django.contrib import messages
from .forms import CommentForm
from urllib.parse import urlparse
from django.urls import reverse
from django.db.models.functions import Lower, RowNumber


def project_list(request):
    project_qs = Project.objects.all().order_by('-created_at')

    # Filters
    search = request.GET.get('search', '').strip()
    skill_ids = request.GET.getlist('skills')  # expects list of Skill IDs

    if search:
        project_qs = project_qs.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    if skill_ids:
        project_qs = project_qs.filter(skills__in=skill_ids).distinct()

    # Pagination
    paginator = Paginator(project_qs, 6)  # Show 6 projects per page
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    # Real-time metrics
    total_projects = Project.objects.count()
    total_skills = Skill.objects.filter(projects__isnull=False).distinct().count()
    filtered_projects_count = project_qs.count()
    filtered_skills_count = Skill.objects.filter(projects__in=project_qs).distinct().count()

    # Preserve query params (without page) for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        query_params.pop('page')
    querystring = query_params.urlencode()

    # Skills for filter UI
    all_skills = Skill.objects.all().order_by('name')

    return render(request, 'portfolio/project_list.html', {
        'projects': projects,
        'total_projects': total_projects,
        'total_skills': total_skills,
        'filtered_projects_count': filtered_projects_count,
        'filtered_skills_count': filtered_skills_count,
        'all_skills': all_skills,
        'selected_skill_ids': list(map(int, skill_ids)) if skill_ids else [],
        'search_query': search,
        'querystring': querystring,
    })


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

        if is_ajax or request.headers.get('HX-Request'):
            context = {
                'comment': comment,
                'project': project,
                'user': request.user,
            }
            # If replying, return the updated parent comment; else return the new comment
            if parent_id:
                parent_comment = comment.parent_comment
                parent_comment._request_user = request.user
                html = render_to_string('portfolio/includes/comment.html',
                                        {'comment': parent_comment, 'project': project},
                                        request=request)
            else:
                comment._request_user = request.user
                html = render_to_string('portfolio/includes/comment.html',
                                        context,
                                        request=request)
            # HTMX: return raw HTML; AJAX: wrap in JSON
            if request.headers.get('HX-Request'):
                return HttpResponse(html)
            else:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Comment posted successfully' if comment.status == 'approved' else 'Your comment is pending approval',
                    'html': html,
                    'comment_id': comment.id,
                })

        if comment.status == 'approved':
            messages.success(request, 'Comment posted successfully')
        else:
            messages.info(request, 'Your comment has been submitted and is pending approval. It will be visible once approved by the administrator.')
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
    comment = get_object_or_404(ProjectComment, pk=pk)

    # Permission check
    if request.user != comment.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        messages.error(request, 'Permission denied')
        return redirect('portfolio:project_detail', pk=comment.project_id)

    text = request.POST.get('text', '').strip()
    if not text:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        messages.error(request, 'Comment text is required')
        return redirect('portfolio:project_detail', pk=comment.project_id)

    try:
        comment.text = text
        comment.is_edited = True
        comment.save()

        # HTMX partial update
        if request.headers.get('HX-Request'):
            comment._request_user = request.user
            html = render_to_string('portfolio/includes/comment.html',
                                    {'comment': comment, 'project': comment.project},
                                    request=request)
            return HttpResponse(html)
        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'text': comment.text, 'is_edited': True})
        # Non-AJAX redirect
        messages.success(request, 'Comment updated successfully')
        return redirect('portfolio:project_detail', pk=comment.project_id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Error updating comment: {str(e)}')
        return redirect('portfolio:project_detail', pk=comment.project_id)


@login_required
@require_POST
def delete_comment(request, pk):
    """Delete a comment."""
    comment = get_object_or_404(ProjectComment, pk=pk)

    if request.user != comment.user and request.user != comment.project.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        messages.error(request, 'Permission denied')
        return redirect('portfolio:project_detail', pk=comment.project_id)

    try:
        project_id = comment.project_id
        comment.delete()
        # HTMX: return empty body; the client will swap out via outerHTML
        if request.headers.get('HX-Request'):
            return HttpResponse('')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        messages.success(request, 'Comment deleted successfully')
        return redirect('portfolio:project_detail', pk=project_id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Error deleting comment: {str(e)}')
        return redirect('portfolio:project_detail', pk=comment.project_id)


@login_required
@require_POST
def toggle_like(request, pk):
    """Toggle like status on a comment."""
    comment = get_object_or_404(ProjectComment, pk=pk)

    try:
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True

        # HTMX behavior: return updated comment HTML
        if request.headers.get('HX-Request'):
            comment._request_user = request.user
            html = render_to_string('portfolio/includes/comment.html',
                                    {'comment': comment, 'project': comment.project},
                                    request=request)
            return HttpResponse(html)
        # AJAX behavior
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'liked': liked, 'likes_count': comment.get_like_count()})
        # Non-AJAX redirect
        return redirect('portfolio:project_detail', pk=comment.project_id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f'Error toggling like: {str(e)}')
        return redirect('portfolio:project_detail', pk=comment.project_id)


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

    # Compute a safe back URL based on referrer (home vs project list pages)
    referrer = request.META.get('HTTP_REFERER', '')
    back_url = reverse('portfolio:home')
    try:
        if referrer:
            parsed = urlparse(referrer)
            if parsed.netloc == request.get_host():
                ref_path = parsed.path
                # Any page under /projects should go back to that exact page (preserve filters/pagination)
                if ref_path.startswith('/projects'):
                    back_url = referrer
                # Explicitly handle home
                elif ref_path == reverse('portfolio:home') or ref_path == '/':
                    back_url = reverse('portfolio:home')
    except Exception:
        back_url = reverse('portfolio:home')

    context = {
        'project': project,
        'comments': comments,
        'comment_form': form,
        'back_url': back_url,
    }
    return render(request, 'portfolio/project_detail.html', context)


def projects_by_skill(request, skill_slug):
    skill_name = skill_slug.replace('-', ' ')
    try:
        # Get all skills with the given name and combine their projects
        skills = Skill.objects.filter(name__iexact=skill_name)
        project_qs = Project.objects.filter(skills__in=skills).distinct().order_by('-created_at')
        paginator = Paginator(project_qs, 6)  # Show 6 projects per page

        page = request.GET.get('page')
        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        filtered_projects_count = project_qs.count()
        filtered_skills_count = Skill.objects.filter(projects__in=project_qs).distinct().count()
    except Skill.DoesNotExist:
        projects = Project.objects.none()
        filtered_projects_count = 0
        filtered_skills_count = 0

    context = {
        'projects': projects,
        'skill_name': skill_name,
        # Overall metrics
        'total_projects': Project.objects.count(),
        'total_skills': Skill.objects.filter(projects__isnull=False).distinct().count(),
        # Filter-specific metrics
        'filtered_projects_count': filtered_projects_count,
        'filtered_skills_count': filtered_skills_count,
    }
    return render(request, 'portfolio/project_list.html', context)


def skill_list(request):
    search = request.GET.get('search', '').strip()

    # Get all skills first for search
    all_skills = Skill.objects.all()
    
    # Apply search filter if provided
    if search:
        search_terms = search.split()
        query = Q()
        for term in search_terms:
            query &= (Q(name__icontains=term) | Q(description__icontains=term))
        all_skills = all_skills.filter(query)

    # Deduplicate by lowercased name, keep the highest proficiency (tie-break by id)
    deduped = (
        all_skills
        .annotate(lower_name=Lower('name'))
        .annotate(
            rn=Window(
                expression=RowNumber(),
                partition_by=[F('lower_name')],
                order_by=[F('proficiency').desc(), F('id').asc()],
            )
        )
        .filter(rn=1)
        .order_by('-proficiency', 'name')  # High → low, then A→Z
    )

    # Pagination
    paginator = Paginator(deduped, 12)
    page_number = request.GET.get('page')
    try:
        skills = paginator.page(page_number)
    except PageNotAnInteger:
        skills = paginator.page(1)
    except EmptyPage:
        skills = paginator.page(paginator.num_pages)

    # Preserve other query params (without page)
    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'portfolio/skill_list.html', {
        'skills': skills,
        'search_query': search,
        'querystring': query_params.urlencode(),
    })


def education_list(request):
    educations = Education.objects.all().order_by('-start_date')
    return render(request, 'portfolio/education_list.html', {'educations': educations})


def experience_list(request):
    experiences = Experience.objects.all().order_by('-start_date')
    return render(request, 'portfolio/experience_list.html', {'experiences': experiences})


def experience_detail(request, pk):
    experience = get_object_or_404(Experience, pk=pk)

    # Prefer manually selected related projects; fall back to skill-based matching
    manual_related = experience.related_projects.all()
    if manual_related.exists():
        related_projects = manual_related.order_by('-created_at')
    else:
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
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Basic validation
        if not all([name, email, subject, message]):
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please fill in all fields.'
                }, status=400)
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'portfolio/contact.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })

        try:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your message has been sent successfully!'
                })

            messages.success(request, 'Your message has been sent successfully!')
            return redirect('portfolio:contact')
        except Exception:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': 'An error occurred while sending your message. Please try again.'
                }, status=500)
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
    projects = Project.objects.all().order_by('id')[:3]
    experiences = Experience.objects.all().order_by('-start_date')[:3]
    educations = Education.objects.all().order_by('-start_date')
    total_skills = Skill.objects.all()

    # Get unique lowercase skill names with their max proficiency
    unique_skills = Skill.objects.annotate(
        lower_name=Lower('name')
    ).values('lower_name').annotate(
        max_proficiency=Max('proficiency')
    ).order_by('-max_proficiency')

    # Get the full skill objects for the unique names with max proficiency
    skill_ids = []
    seen_names = set()

    for skill in unique_skills[:8]:  # Limit to top 8 skills for the home page
        skill_obj = Skill.objects.filter(
            name__iexact=skill['lower_name'],
            proficiency=skill['max_proficiency']
        ).first()

        if skill_obj and skill_obj.name.lower() not in seen_names:
            seen_names.add(skill_obj.name.lower())
            skill_ids.append(skill_obj.id)

    # Get the actual skill objects in the correct order
    skills = Skill.objects.filter(id__in=skill_ids).order_by('-proficiency')
    latest_resume = Resume.objects.first()

    return render(request, 'portfolio/home.html', {
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
        'latest_resume': latest_resume,
        'total_skills': total_skills,
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
