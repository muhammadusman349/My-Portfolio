from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.


class Skill(models.Model):
    PROFICIENCY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Elementary'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    proficiency = models.IntegerField(choices=PROFICIENCY_CHOICES)

    def __str__(self):
        return f"{self.name} - {self.get_proficiency_display()}"

    @property
    def proficiency_percent(self) -> int:
        """Return proficiency as a percentage in 20% steps (1->20, 5->100)."""
        try:
            return int(self.proficiency) * 20
        except Exception:
            return 0

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Skills'


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, related_name='projects', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    github_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='project_images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"Image for {self.project.title}"


class ProjectComment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_owner_reply = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    likes = models.ManyToManyField(get_user_model(), related_name='liked_comments', blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.project.title}'

    def get_replies(self):
        return self.replies.all()

    def get_reply_count(self):
        return self.replies.count()

    def get_like_count(self):
        return self.likes.count()

    def is_liked_by_user(self, user=None):
        if not user or not user.is_authenticated:
            return False
        return self.likes.filter(id=user.id).exists()

    def get_time_since(self):
        now = timezone.now()
        diff = now - self.created_at

        if diff.days > 365:
            years = diff.days // 365
            return f'{years}y ago'
        elif diff.days > 30:
            months = diff.days // 30
            return f'{months}mo ago'
        elif diff.days > 0:
            return f'{diff.days}d ago'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'{hours}h ago'
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f'{minutes}m ago'
        else:
            return 'just now'

    def get_nesting_level(self):
        """Calculate the nesting level of this comment."""
        level = 0
        current = self
        while current.parent_comment:
            level += 1
            current = current.parent_comment
        return level


class Education(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.degree} at {self.institution}'

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Education'


class Experience(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('CT', 'Contract'),
        ('FE', 'Freelance'),
        ('IN', 'Internship'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=2, choices=EMPLOYMENT_TYPE_CHOICES, default='FT')
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(help_text="Describe your responsibilities and achievements")
    technologies_used = models.ManyToManyField(Skill, blank=True, help_text="Select relevant skills")
    company_url = models.URLField(blank=True)
    # Manually associate related projects for this experience
    related_projects = models.ManyToManyField(
        Project,
        blank=True,
        related_name='related_experiences',
        help_text='Select projects that are directly related to this experience'
    )

    def __str__(self):
        return f'{self.position} at {self.company}'

    def save(self, *args, **kwargs):
        if self.current:
            self.end_date = None
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = 'Experience'


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.name} - {self.subject}'

    class Meta:
        ordering = ['-created_at']


class Resume(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resume/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Resume ({self.user.username}) - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"
