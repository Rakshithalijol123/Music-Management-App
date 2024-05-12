from django.urls import path
from .views import SongListCreateAPIView, PlaylistListCreateAPIView, PlaylistDetailUpdateAPIView, PlaylistSongsListAPIView, MovePlaylistSongAPIView, RemovePlaylistSongAPIView

urlpatterns = [
    path('songs/', SongListCreateAPIView.as_view(), name='song-list-create'),
    path('playlists/', PlaylistListCreateAPIView.as_view(), name='playlist-list-create'),
    path('playlists/<int:pk>/', PlaylistDetailUpdateAPIView.as_view(), name='playlist-detail-update'),
    path('playlists/<int:playlist_id>/songs/', PlaylistSongsListAPIView.as_view(), name='playlist-songs-list'),
    path('playlists/<int:playlist_id>/songs/<int:song_id>/move/', MovePlaylistSongAPIView.as_view(), name='move-playlist-song'),  # Updated URL pattern
    path('playlists/<int:playlist_id>/songs/<int:song_id>/remove/', RemovePlaylistSongAPIView.as_view(), name='remove-playlist-song'),  # Updated URL pattern
]
