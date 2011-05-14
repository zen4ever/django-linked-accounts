from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    username = forms.RegexField(
        max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text="""
        Required. 30 characters or fewer.
        Letters, digits and @/./+/-/_ only.
        """,
        error_messages={
            'invalid': "This value may contain only letters, "
                       "numbers and @/./+/-/_ characters."
        }
    )
    email = forms.EmailField()

    def clean_username(self):
        data = self.cleaned_data['username']
        try:
            User.objects.get(username=data)
            raise forms.ValidationError(
                "User with this username already exists"
            )
        except User.DoesNotExist:
            return data

    def clean_email(self):
        data = self.cleaned_data['email']
        try:
            User.objects.get(email=data)
            raise forms.ValidationError(
                "User with this email already exists"
            )
        except User.DoesNotExist:
            return data

    def save(self, profile):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email']
        )
        profile.user = user
        profile.save()
        return user
