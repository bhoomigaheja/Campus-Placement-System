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
        user.is_active = False # Require email verification
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
        user.is_active = False # Require email verification
        user.username = self.cleaned_data.get('email')
        if commit:
            user.save()
            CompanyProfile.objects.create(user=user, company_name=self.cleaned_data.get('company_name'))
        return user

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True, label="Email Address", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

        if password:
            if len(password) < 8:
                self.add_error('password', "Password must be at least 8 characters long.")
            if not any(char.isupper() for char in password):
                self.add_error('password', "Password must contain at least one uppercase letter.")
            if not any(char.islower() for char in password):
                self.add_error('password', "Password must contain at least one lowercase letter.")
            if not any(char.isdigit() for char in password):
                self.add_error('password', "Password must contain at least one number.")

        return cleaned_data

from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "Please verify your email address before logging in. |UNVERIFIED|",
                code='inactive',
            )
        super().confirm_login_allowed(user)
