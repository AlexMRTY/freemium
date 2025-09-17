import spotipy
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import json
from pydantic import BaseModel

load_dotenv()

class SpotifyTrack(BaseModel):
  id: str
  name: str
  trackArtists: list[str]
  albumArtists: list[str]
  albumName: str
  durationMs: int
  albumImageUrl: str | None

class SpotifyApi():
    def __init__(self):
        self.sp_credential = SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                       client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"))
        self.sp = spotipy.Spotify(auth_manager=self.sp_credential)

    def search_track(self, query: str, limit: int = 5) -> list[SpotifyTrack]:
        results = self.sp.search(q=query, limit=limit, type='track')
        
        if not results or 'tracks' not in results or 'items' not in results['tracks']:
            return []
        
        tracks = []
        for item in results['tracks']['items']:
            track = SpotifyTrack(
                id=item['id'],
                name=item['name'],
                trackArtists=[artist['name'] for artist in item['artists']],
                albumArtists=[artist['name'] for artist in item['album']['artists']],
                albumName=item['album']['name'],
                durationMs=item['duration_ms'],
                albumImageUrl=item['album']['images'][0]['url'] if item['album']['images'] else None
            )
            tracks.append(track)
        return tracks
