from rest_framework import generics
from .models import Song, Playlist
from .serializers import SongSerializer, PlaylistSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SongListCreateAPIView(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PlaylistListCreateAPIView(generics.ListCreateAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class PlaylistDetailUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    

class PlaylistSongsListAPIView(generics.ListAPIView):
    serializer_class = SongSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['position']

    def get_queryset(self):
        playlist_id = self.kwargs['playlist_id']
        return Song.objects.filter(playlist__id=playlist_id).order_by('id')
    

class MovePlaylistSongAPIView(generics.UpdateAPIView):
    queryset = Song.objects.all()
    lookup_url_kwarg = 'song_id'

    def put(self, request, *args, **kwargs):
        song_id = kwargs.get('song_id')
        playlist_id = kwargs.get('playlist_id')
        
        try:
            song = Song.objects.get(id=song_id, playlist_id=playlist_id)
        except Song.DoesNotExist:
            return Response({'detail': 'Song not found in the playlist'}, status=status.HTTP_404_NOT_FOUND)
        
        new_position = int(request.data.get('position'))
        current_position = song.position

        # Adjust positions for other songs in the playlist
        if new_position < current_position:
            songs_to_update = Song.objects.filter(playlist_id=playlist_id, position__gte=new_position, position__lt=current_position)
            shift_value = 1
        elif new_position > current_position:
            songs_to_update = Song.objects.filter(playlist_id=playlist_id, position__gt=current_position, position__lte=new_position)
            shift_value = -1
        else:
            return Response({'detail': 'New position is same as the current position'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update positions for affected songs
        for song_to_update in songs_to_update:
            song_to_update.position += shift_value
            song_to_update.save()

        # Move the song to the new position
        song.position = new_position
        song.save()

        return Response({'position': new_position}, status=status.HTTP_200_OK)
    
    
class RemovePlaylistSongAPIView(generics.DestroyAPIView):
    queryset = Song.objects.all()
    lookup_url_kwarg = 'song_id'

    def delete(self, request, *args, **kwargs):
        song_id = kwargs.get('song_id')

        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({'detail': 'Song not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the position of the song
        song_position = song.position
        playlist_id = song.playlist_id

        # Delete the song from the playlist
        song.delete()

        # Adjust positions for other songs in the playlist
        songs_to_update = Song.objects.filter(playlist_id=playlist_id, position__gt=song_position)
        for song_to_update in songs_to_update:
            song_to_update.position -= 1
            song_to_update.save()

        return Response(status=status.HTTP_200_OK)
