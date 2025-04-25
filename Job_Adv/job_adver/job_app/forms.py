from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,Job,Profile
from django.contrib.auth.forms import AuthenticationForm
from .models import JobApplication

class EmployerRegistrationForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2','profile_picture']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employer'
        if commit:
            user.save()
        return user

class EmployeeRegistrationForm(UserCreationForm):
    profile_picture = forms.ImageField(required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2','profile_picture']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'employee'
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


# post_job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['JobRole', 'company', 'location', 'category', 'description']

        widgets = {
            'JobRole': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),  
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}), 
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']


# forms.py

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
