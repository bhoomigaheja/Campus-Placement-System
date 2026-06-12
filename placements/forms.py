from django import forms
from .models import Job, Application, Interview
from accounts.models import CompanyProfile

class CompanyForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Company login email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text="Company login password")

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'email', 'password', 'website', 'industry']

class JobForm(forms.ModelForm):
    company_name = forms.CharField(
        label="Company Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Google, Stripe'})
    )
    
    required_skills = forms.CharField(
        label="Required Skills",
        required=False,
        widget=forms.TextInput(attrs={
            'data-tags-input': 'true',
            'placeholder': 'Type skill and press Enter...',
            'class': 'form-control'
        }),
        help_text="Type a skill and press Enter. Supports both predefined and custom skills."
    )

    class Meta:
        model = Job
        fields = ['title', 'employment_type', 'location', 'salary_package', 'min_cgpa', 'eligible_branches', 'deadline_to_apply', 'description']
        widgets = {
            'deadline_to_apply': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
            'employment_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-time, Internship'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote, Bangalore, San Francisco'}),
            'salary_package': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. $120k/yr or 15 LPA'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the role, responsibilities, and benefits...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.company:
                self.initial['company_name'] = self.instance.company.company_name
            self.initial['required_skills'] = ", ".join([s.name for s in self.instance.required_skills.all()])

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not CompanyProfile.objects.filter(company_name=company_name).exists():
            raise forms.ValidationError("Please select a valid registered company.")
        return company_name

    def clean_deadline_to_apply(self):
        deadline = self.cleaned_data.get('deadline_to_apply')
        from django.utils import timezone
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("The deadline must be in the future.")
        return deadline

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        
        # Save required skills
        from students.models import Skill
        skills_str = self.cleaned_data.get('required_skills', '')
        skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        skill_objects = []
        for name in skill_names:
            skill, created = Skill.objects.get_or_create(name=name)
            skill_objects.append(skill)
        instance.required_skills.set(skill_objects)
        
        self.save_m2m()
        return instance

class CompanyJobForm(forms.ModelForm):
    required_skills = forms.CharField(
        label="Required Skills",
        required=False,
        widget=forms.TextInput(attrs={
            'data-tags-input': 'true',
            'placeholder': 'Type skill and press Enter...',
            'class': 'form-control'
        }),
        help_text="Type a skill and press Enter. Supports both predefined and custom skills."
    )

    class Meta:
        model = Job
        fields = ['title', 'employment_type', 'location', 'salary_package', 'min_cgpa', 'eligible_branches', 'deadline_to_apply', 'description']
        widgets = {
            'deadline_to_apply': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Software Engineer'}),
            'employment_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Full-time, Internship'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Remote, Bangalore'}),
            'salary_package': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15 LPA'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the role...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['required_skills'] = ", ".join([s.name for s in self.instance.required_skills.all()])

    def clean_deadline_to_apply(self):
        deadline = self.cleaned_data.get('deadline_to_apply')
        from django.utils import timezone
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("The deadline must be in the future.")
        return deadline

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        
        # Save required skills
        from students.models import Skill
        skills_str = self.cleaned_data.get('required_skills', '')
        skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        skill_objects = []
        for name in skill_names:
            skill, created = Skill.objects.get_or_create(name=name)
            skill_objects.append(skill)
        instance.required_skills.set(skill_objects)
        
        self.save_m2m()
        return instance

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class CompanyApplicationUpdateForm(forms.ModelForm):
    interview_mode = forms.ChoiceField(
        label="Interview Mode",
        choices=[('ONLINE', 'Online (Virtual)'), ('IN_PERSON', 'In-Person (Physical)')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_interview_mode'})
    )
    interview_meeting_link = forms.URLField(
        label="Meeting Link (Zoom / Google Meet)",
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://meet.google.com/abc-defg-hij', 'id': 'id_interview_meeting_link'})
    )
    interview_venue = forms.CharField(
        label="Physical Venue Address / Location",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Placement Seminar Hall, Room 302', 'id': 'id_interview_venue'})
    )
    interview_scheduled_at = forms.DateTimeField(
        label="Interview Date & Time",
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    interview_notes = forms.CharField(
        label="Interview Notes / Instructions",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Instructions for the candidate (e.g. bring project files)'})
    )

    class Meta:
        model = Application
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-lg', 'id': 'id_status'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional internal remarks about the candidate...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                interview = self.instance.interview
                self.initial['interview_mode'] = interview.interview_mode
                if interview.scheduled_at:
                    self.initial['interview_scheduled_at'] = interview.scheduled_at.strftime('%Y-%m-%dT%H:%M')
                if interview.interview_mode == 'ONLINE':
                    self.initial['interview_meeting_link'] = interview.meeting_link
                else:
                    self.initial['interview_venue'] = interview.meeting_link
                self.initial['interview_notes'] = interview.notes
            except Exception:
                pass

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['scheduled_at', 'meeting_link', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class TPOCompanyEditForm(forms.ModelForm):
    # User model fields
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    contact_person = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. John Doe'}))
    
    # Optional password reset
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
        help_text="Provide a new password if you want to reset it."
    )

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'industry', 'website', 'description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['contact_person'].initial = f"{self.user.first_name} {self.user.last_name}".strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This email is already in use by another account.")
        return email
