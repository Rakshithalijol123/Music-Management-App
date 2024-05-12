from rest_framework import serializers
from .models import Song, Playlist

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'name', 'artist', 'release_year']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name', 'songs']

