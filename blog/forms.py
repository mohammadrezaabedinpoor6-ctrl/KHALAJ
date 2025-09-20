from django import forms
from django.core.validators import FileExtensionValidator
from . import models


class blogForm(forms.ModelForm):
    class Meta:
        model = models.Blog
        fields = ['title', 'description', 'cover', 'audio']


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ('text',)


class ReplyForm(forms.ModelForm):
    class Meta:
        model = models.Reply
        fields = ('text',)