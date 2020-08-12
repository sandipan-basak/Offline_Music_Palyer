# from django.conf.urls import url
from django.urls import path
from OfflinePlaylist import views

app_name = 'OfflinePlaylist'

urlpatterns = [
    path(r'^$', views.index, name="index"),
    path(r'^playlists/', views.playlists, name = 'playlist'),
    path(r'^test/', views.test, name = 'test'),
]