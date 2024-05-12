from django.db import models

class Song(models.Model):
    name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    release_year = models.IntegerField()

    def __str__(self):
        return self.name

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    songs = models.ManyToManyField('Song')

    def __str__(self):
        return self.name
