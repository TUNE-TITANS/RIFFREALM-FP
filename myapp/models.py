from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    genres = models.CharField(max_length=200, blank=True)
    artists = models.CharField(max_length=200, blank=True)
    song_types = models.CharField(max_length=200, blank=True)

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200)
    albumCover = models.URLField()
    spotifyUrl = models.URLField()
    genre = models.CharField(max_length=200)
    # other fields as required

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Playlist(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return self.name

