from django.urls import path
from . import views

app_name = 'songs'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('songs/submit/', views.submit_song, name='submit'),
    path('songs/<int:pk>/', views.song_detail, name='detail'),
    path('songs/<int:pk>/rate/', views.rate_song, name='rate'),
    path('songs/<int:pk>/comment/', views.add_comment, name='add_comment'),
]
