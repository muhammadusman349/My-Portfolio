from portfolio.models import ProjectComment

def dashboard_context(request):
    if not request.user.is_authenticated:
        return {}
        
    return {
        'unread_comments_count': ProjectComment.objects.filter(is_read=False).count()
    }
