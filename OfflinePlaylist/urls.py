# from django.conf.urls import url
from django.urls import path
from OfflinePlaylist import views

app_name = 'OfflinePlaylist'

urlpatterns = [
    path('', views.index, name="index"),
    path('playlist/', views.playlists, name='playlists'),
    path('test/', views.test, name='test'),
    path('GetPlaylists/', views.get_playlist, name='GetPlaylists'),
    path('song/<int:pk>', views.song_view, name='curr_song')
]