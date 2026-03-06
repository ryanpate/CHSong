from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404

from .models import Song, Rating, Comment
from .forms import SongForm, RatingForm, CommentForm


def dashboard(request):
    songs = Song.objects.filter(is_approved=True).annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings', distinct=True),
        comment_count=Count('comments', distinct=True),
    )

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        songs = songs.filter(title__icontains=q) | songs.filter(artist__icontains=q)

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'top_rated':
        songs = songs.order_by('-avg_rating')
    elif sort == 'most_comments':
        songs = songs.order_by('-comment_count')
    else:
        songs = songs.order_by('-submitted_at')

    return render(request, 'songs/dashboard.html', {
        'songs': songs,
        'q': q,
        'sort': sort,
    })


@login_required
def submit_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            song = form.save(commit=False)
            song.submitted_by = request.user
            song.save()
            return redirect('songs:dashboard')
    else:
        form = SongForm()
    return render(request, 'songs/submit_song.html', {'form': form})


def song_detail(request, pk):
    song = get_object_or_404(Song, pk=pk)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(song=song, user=request.user).first()

    top_level_comments = song.comments.filter(parent__isnull=True).select_related('user').prefetch_related('replies__user')
    comment_form = CommentForm()
    rating_form = RatingForm()

    return render(request, 'songs/song_detail.html', {
        'song': song,
        'user_rating': user_rating,
        'comments': top_level_comments,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'avg_rating': song.ratings.aggregate(avg=Avg('stars'))['avg'],
        'rating_count': song.ratings.count(),
    })


@login_required
def rate_song(request, pk):
    if request.method == 'POST':
        song = get_object_or_404(Song, pk=pk)
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                song=song,
                user=request.user,
                defaults={'stars': form.cleaned_data['stars']},
            )
    return redirect('songs:detail', pk=pk)


@login_required
def add_comment(request, pk):
    if request.method == 'POST':
        song = get_object_or_404(Song, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = form.cleaned_data.get('parent')
            parent = None
            if parent_id:
                parent = Comment.objects.filter(pk=parent_id, song=song).first()
            Comment.objects.create(
                song=song,
                user=request.user,
                parent=parent,
                body=form.cleaned_data['body'],
            )
    return redirect('songs:detail', pk=pk)
