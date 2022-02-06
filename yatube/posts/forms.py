from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'group', 'image')


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Текст комментария',
                'rows': '6',
            }
        )
    )

    class Meta:
        model = Comment
        fields = ('text',)
