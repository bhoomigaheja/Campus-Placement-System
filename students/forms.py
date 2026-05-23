from django import forms
from accounts.models import StudentProfile
from students.models import Skill

class StudentProfileForm(forms.ModelForm):
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'data-tags-input': 'true',
            'placeholder': 'Type skill and press Enter...',
            'class': 'form-control'
        }),
        help_text="Type a skill and press Enter. Supports both predefined and custom skills."
    )

    projects = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your major projects...'}),
        required=False,
        help_text="Mention your key projects (tech, description, role)"
    )

    internships = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add your internships or work experience...'}),
        required=False,
        help_text="Add your internships or work experience"
    )

    class Meta:
        model = StudentProfile
        fields = ['branch', 'cgpa', 'resume', 'projects', 'internships']
        widgets = {
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['skills'] = ", ".join([s.name for s in self.instance.skills.all()])

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Safe resume file handling: delete old resume if a new one is uploaded
        if 'resume' in self.changed_data and self.instance.pk:
            try:
                old_instance = StudentProfile.objects.get(pk=self.instance.pk)
                if old_instance.resume and old_instance.resume != instance.resume:
                    from core.utils.media_utils import MediaHelper
                    MediaHelper.safe_delete(old_instance.resume)
            except Exception:
                pass

        if commit:
            instance.save()
        
        # Save skills
        skills_str = self.cleaned_data.get('skills', '')
        skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        skill_objects = []
        for name in skill_names:
            skill, created = Skill.objects.get_or_create(name=name)
            skill_objects.append(skill)
        instance.skills.set(skill_objects)
        
        self.save_m2m()
        return instance