# from datetime import datetime
from django.db import models

# Create your models here.  

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # value = models.CharField(max_length=10, default=False)
    class Meta():
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name

class Playlists(models.Model):
    name = models.CharField(max_length=150, unique=True)
    created = models.DateTimeField(default='')

    def __str__(self):
        return self.name

    class Meta():
        ordering = ['name']

class Song(models.Model):
    track_name = models.CharField(max_length=100)
    artist_name = models.CharField(max_length=100)
    album_name = models.CharField(max_length=100)
    video_file = models.CharField(max_length=150, null=True, default='')
    playlist = models.ForeignKey(to=Playlists, on_delete=models.CASCADE)
    downloaded = models.BooleanField(default=False)

    def __str__(self):
        return self.track_name

class DownloadedSongs(models.Model):
    song_name = models.CharField(max_length=150, unique=True)
    artist_name = models.CharField(max_length=150)

class Track(models.Model):
    name = models.CharField(primary_key=True, max_length=100, unique=True)
    album = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    id = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Album(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True)
    name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Artist(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
