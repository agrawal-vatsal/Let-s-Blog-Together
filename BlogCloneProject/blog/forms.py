from django import forms
from . import models
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    class Meta():
        model = models.Post
        fields = ('title', 'text')
        widgets = {'title': forms.TextInput(attrs={'class': 'textinputclass'}),
                   'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'})}


class CommentForm(forms.ModelForm):
    class Meta():
        model = models.Comment
        fields = ('author', 'text')
        widgets = {'author': forms.TextInput(attrs={'class': 'textinputclass'}),
                   'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})}


class UserCommentForm(forms.ModelForm):
    class Meta():
        model = models.Comment
        fields = {'text'}
        widgets = {'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'})}


class UserForm(forms.ModelForm):
    class Meta():
        model = User
        fields = {'first_name', 'last_name', 'username', 'email'}

        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            self.fields.keyOrder = ['first_name', 'last_name', 'username', 'email']



class UserPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Enter your password')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Enter your password again')

    def clean(self):
        allClean = super().clean()
        pass1 = allClean['password1']
        pass2 = allClean['password2']
        if pass1 != pass2:
            raise forms.ValidationError('Passwords do not match')


class loginForm(forms.Form):
    username = forms.CharField(max_length=250)
    password = forms.CharField(widget=forms.PasswordInput())
