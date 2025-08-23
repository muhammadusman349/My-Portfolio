from django import forms
from .models import (
    Project, Skill, Education,
    Experience, ProjectComment,
    ProjectImage, Resume
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'skills', 'github_link', 'live_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.SelectMultiple(attrs={
                'class': 'form-multiselect block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300'
            }),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-40 h-8 text-sm rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300'
            }),
            'proficiency': forms.Select(choices=Skill.PROFICIENCY_CHOICES, attrs={
                'class': 'form-select w-40 h-8 text-sm rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300'
            }),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'employment_type', 'location', 'start_date', 'end_date',
                 'current', 'description', 'technologies_used', 'company_url']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'technologies_used': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get('current')
        end_date = cleaned_data.get('end_date')

        if current and end_date:
            raise forms.ValidationError("End date should be empty if this is your current position")
        elif not current and not end_date:
            raise forms.ValidationError("Please provide an end date for past positions")

        return cleaned_data


class ContactResponseForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'w-full p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': '6',
                'placeholder': 'Write your response to the contact message...'
            }
        ),
        required=True,
        help_text='This response will be sent to the contact\'s email address.'
    )


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:border-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
            'rows': '4',
            'placeholder': 'Write your reply here...'
        }),
        label='',
    )

    class Meta:
        model = ProjectComment
        fields = ['text']


class CommentResponseForm(forms.Form):
    response = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white',
                'rows': '4',
                'placeholder': 'Write your response...'
            }
        ),
        required=True
    )


class ProjectImageForm(forms.ModelForm):
    class Meta:
        model = ProjectImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'caption': forms.TextInput(attrs={
                'class': 'form-input block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300',
                'placeholder': 'Image caption (optional)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-input block w-20 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300',
                'min': '0'
            })
        }


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-300 dark:bg-gray-700 dark:border-gray-600',
                'accept': '.pdf,.doc,.docx'
            })
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            raise forms.ValidationError('Please select a file to upload.')
        if f.size and f.size > 10 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 10MB).')
        valid_exts = ['.pdf', '.doc', '.docx']
        name = (f.name or '').lower()
        if not any(name.endswith(ext) for ext in valid_exts):
            raise forms.ValidationError('Invalid file type. Allowed: PDF, DOC, DOCX.')
        return f
