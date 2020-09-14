# from django.conf.urls import url
from django.urls import path
from OfflinePlaylist import views

app_name = 'OfflinePlaylist'

urlpatterns = [
    path('', views.index, name="index"),
    path('playlists/', views.playlists, name='playlists'),
    path('test/', views.test, name='test'),
    path('GetPlaylists/', views.get_playlist, name='GetPlaylists'),
]