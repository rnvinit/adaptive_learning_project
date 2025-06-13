# forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
import re
from core_app.models import UserProfile

# -------------------------
# Password Strength Checker
# -------------------------
def validate_password_strength(password):
    """
    Validates that the password meets strength requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")

# -------------------------
# Base Signup Form
# -------------------------
class BaseSignupForm(UserCreationForm):
    """
    A base signup form with name, email, username, and password fields.
    Used as a parent for both StudentSignupForm and EducatorSignupForm.
    """
    name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your full name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your email address'
    }))

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Create a password'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-input',
                'placeholder': 'Confirm password'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password_strength(password1)
        return password1

# -------------------------
# Student Signup Form
# -------------------------
class StudentSignupForm(BaseSignupForm):
    """
    Signup form for students.
    Assigns the 'student' user_type in UserProfile.
    """
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, user_type='student')
        return user

# -------------------------
# Educator Signup Form
# -------------------------
class EducatorSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Get or create the user profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'user_type': 'educator'}
            )
            if not created:
                profile.user_type = 'educator'
                profile.save()
        return user
# -------------------------
# Base Login Form
# -------------------------

class BaseLoginForm(AuthenticationForm):
    """
    Base login form with consistent styling.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your username',
        'autofocus': True
    }))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Your password',
        'autocomplete': 'current-password'
    }))

    error_messages = {
        'invalid_login': "Please enter a correct username and password.",
        'inactive': "This account is inactive.",
    }

# -------------------------
# Student Login Form
# -------------------------
class StudentLoginForm(BaseLoginForm):
    """
    Login form for students.
    """
    pass

# -------------------------
# Educator Login Form
# -------------------------
class EducatorLoginForm(BaseLoginForm):
    """
    Login form for educators.
    """
    pass
