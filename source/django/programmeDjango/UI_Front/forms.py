from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from .models import CustomUser

class SignForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("email already exist")
        else:
            return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super(LoginForm,self).clean()
        email = data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError("email doesn't exist")
        else:
            return data

    def clean_password(self):
        data = super(LoginForm,self).clean()
        email = data['email']
        password = data['password']
        check = authenticate(email=email,password=password)
        if check is None:
            raise ValidationError("incorrect password")
        else:
            return password

