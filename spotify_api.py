import spotipy
import pprint
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.client import SpotifyException
import os
from dotenv import load_dotenv
import json
from pydantic import BaseModel

load_dotenv()

class Artist(BaseModel):
    id: str
    name: str

class Album(BaseModel):
    id: str
    name: str
    artists: list[Artist]
    imageUrl: str | None = None


class SpotifyTrack(BaseModel):
  id: str
  name: str
  artists: list[Artist]
  album: Album
  durationMs: int

class SpotifyPlaylist(BaseModel):
  id: str
  name: str
  description: str | None
  imageUrl: str | None
  tracks: list[SpotifyTrack]

class SpotifyApi():
    def __init__(self):
        self.sp_client_credential = SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                       client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"))
        self.sp_user_credentials = SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                       client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                                                       redirect_uri="http://127.0.0.1:4000/callback",
                                                       scope="playlist-read-private playlist-read-collaborative")
        self.sp_client = spotipy.Spotify(auth_manager=self.sp_client_credential)
        self.sp_user = spotipy.Spotify(auth_manager=self.sp_user_credentials)

    def get_user_playlists(self) -> list[SpotifyPlaylist] | None:
        try:
            results = self.sp_user.current_user_playlists()
        except SpotifyException as e:
            print(f"Error occurred while fetching user playlists: {e}")
            return None
        if not results: return []

        playlists = []
        for item in results['items']:
            playlist = SpotifyPlaylist(
                id=item['id'],
                name=item['name'],
                description=item['description'],
                imageUrl=item['images'][0]['url'] if item['images'] else None,
                tracks=self.get_playlist_tracks(item['id'])
            )
            playlists.append(playlist)
        return playlists

    

    def get_playlist_tracks(self, playlist_id: str) -> list[SpotifyTrack]:
        try:
            results = self.sp_user.playlist_items(playlist_id)
        except SpotifyException as e:
            print(f"Error occurred while fetching playlist tracks: {e}")
            return []
        
        if not results or 'items' not in results:
            return []
        
        tracks = []
        for item in results['items']:
            track_info = item['track']
            artists = [Artist(id=artist['id'], name=artist['name']) for artist in track_info['artists']]
            album = Album(
                id=track_info['album']['id'],
                name=track_info['album']['name'],
                artists=[Artist(id=artist['id'], name=artist['name']) for artist in track_info['album']['artists']],
                imageUrl=track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
            )
            track = SpotifyTrack(
                id=track_info['id'],
                name=track_info['name'],
                artists=artists,
                album=album,
                durationMs=track_info['duration_ms'],
            )
            tracks.append(track)
        return tracks

    def search_track(self, query: str, limit: int = 5) -> list[SpotifyTrack]:
        try:
            results = self.sp_client.search(q=query, limit=limit, type='track')
        except SpotifyException as e:
            print(f"Error occurred while searching for tracks: {e}")
            return []
        
        
        if not results or 'tracks' not in results or 'items' not in results['tracks']:
            return []
        
        tracks = []
        for item in results['tracks']['items']:
            artists = [Artist(id=artist['id'], name=artist['name']) for artist in item['artists']]
            album = Album(
                id=item['album']['id'],
                name=item['album']['name'],
                artists=[Artist(id=artist['id'], name=artist['name']) for artist in item['album']['artists']],
                imageUrl=item['album']['images'][0]['url'] if item['album']['images'] else None
            )
            track = SpotifyTrack(
                id=item['id'],
                name=item['name'],
                artists=artists,
                album=album,
                durationMs=item['duration_ms'],
            )
            tracks.append(track)
        return tracks


def get_user_playlists_tmp() -> list[SpotifyPlaylist] | None:
    with open("user_playlists_tmp.json", "r") as file:
        data = json.load(file)
    return [SpotifyPlaylist(**playlist) for playlist in data]