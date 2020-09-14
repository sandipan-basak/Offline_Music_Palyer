from django.contrib import admin
from OfflinePlaylist.models import Track, Song, Artist, Album, Category, Playlists, DownloadedSongs

# Register your models here.
admin.site.register(Playlists)
admin.site.register(Song)
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Category)
admin.site.register(DownloadedSongs)
