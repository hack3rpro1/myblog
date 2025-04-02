from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile, Comment, College
from django.core.exceptions import ValidationError
class PostForm(forms.ModelForm):
    image = forms.ImageField(required=False)  # Allow optional image upload

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'college', 'image']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract custom user kwarg
        super().__init__(*args, **kwargs)
        # Hide category and college fields for non-admin users
        if self.user and not self.user.is_staff:
            self.fields['category'].widget = forms.HiddenInput()
            self.fields['college'].widget = forms.HiddenInput()

    def clean_category(self):
        # Ensure that only admins can set the category
        if self.user and not self.user.is_staff:
            raise ValidationError("You do not have permission to select a category.")
        return self.cleaned_data.get('category')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['college', 'department']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class CustomUserCreationForm(UserCreationForm):
    # Allow users to select an existing college and enter a department
    college = forms.ModelChoiceField(
        queryset=College.objects.all(),
        required=True,
        label="College"
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        label="Department (Optional)"
    )

    class Meta:
        model = User
        fields = ("username", "email", "college", "department", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Create a profile with the additional fields
            Profile.objects.create(
                user=user,
                college=self.cleaned_data["college"],
                department=self.cleaned_data.get("department", "")
            )
        return user
