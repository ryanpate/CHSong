from django import forms
from .models import Song, Comment


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'song_link', 'reason']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Song title'}),
            'artist': forms.TextInput(attrs={'placeholder': 'Artist name'}),
            'song_link': forms.URLInput(attrs={'placeholder': 'Link to song (optional)'}),
            'reason': forms.Textarea(attrs={'placeholder': 'Why should we sing this song?', 'rows': 4}),
        }


class RatingForm(forms.Form):
    stars = forms.IntegerField(min_value=1, max_value=5)


class CommentForm(forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Add a comment...', 'rows': 3}))
    parent = forms.IntegerField(required=False, widget=forms.HiddenInput())
