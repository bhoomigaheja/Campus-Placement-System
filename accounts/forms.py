from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.username = self.cleaned_data.get('email') # Username is not used but kept for abstract user compat
        if commit:
            user.save()
        return user

from .models import CompanyProfile

class CompanySignUpForm(UserCreationForm):
    company_name = forms.CharField(max_length=255, required=True, label="Company Name")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'company_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A company with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_company = True
        user.username = self.cleaned_data.get('email')
        if commit:
            user.save()
            CompanyProfile.objects.create(user=user, company_name=self.cleaned_data.get('company_name'))
        return user
