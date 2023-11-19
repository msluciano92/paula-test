from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import *
from django.contrib.auth.models import *
from .models import Community, CustomUser, Comment

class PostForm(forms.Form):
    url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'style-86'}),
        label='URL'
    )

    title = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'style-98', 'required': 'true', 'rows': '1', 'minlength': '3', 'maxlength': '200'}),
        label='Title'
    )

    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'style-98-vis', 'required': 'true', 'rows': '4', 'minlength': '3', 'maxlength': '200'}),
        label='Body'
    )

    community = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'style-98', 'required': 'true', 'rows': '1', 'minlength': '1', 'maxlength': '200'}),
        label='Community'
    )

class EditPostForm(forms.Form):
    url = forms.URLField(
        widget=forms.URLInput(attrs={'class': 'style-86'}),
        label='URL'
    )

    title = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={'class': 'style-98', 'required': 'true', 'rows': '1', 'minlength': '3', 'maxlength': '200'}),
        label='Title'
    )

    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'style-98-vis', 'required': 'true', 'rows': '4', 'minlength': '3', 'maxlength': '200'}),
        label='Body'
    )

    community = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'style-98', 'required': 'true', 'rows': '1', 'minlength': '1', 'maxlength': '200'}),
        label='Community'
    )

class CommunityForm(ModelForm):
    class Meta:
        model= Community
        fields = ['id', 'name', 'banner', 'avatar']

class CustomUserForm(ModelForm):
    class Meta:
        model= CustomUser
        fields = ['name', 'avatar', 'banner', 'description']      

class CommentForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'style-98-vis', 'required': 'true', 'rows': '4', 'minlength': '3', 'maxlength': '200'}),
        label='Body'
    )