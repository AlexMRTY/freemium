from mutagen.id3 import ID3
from mutagen.id3._frames import TIT2, TPE1, TPE2, TALB, TLEN, APIC
from pathlib import Path

from spotify_api import SpotifyTrack
import requests


class AudioFile:
    def __init__(self, path) -> None:
        self.path = Path(path)
        self.audio = ID3(self.path)

    def fetch_image(self, imgUrl: str):
        response = requests.get(imgUrl)
        if response.status_code != 200:
            print(f"Failed to fetch image from URL: {imgUrl}")
            return None, None

        mime_type = response.headers.get("Content-Type", "")
        if mime_type not in ["image/jpeg", "image/png"]:
            print(f"Unsupported image type: {mime_type}")
            return None, None

        return response.content, mime_type

    def modify_art(self, imgUrl: str):
        image_data, mime_type = self.fetch_image(imgUrl)
        if not image_data or not mime_type:
            return

        image = APIC(
            encoding=3,
            mime=mime_type,
            type=3,
            desc="Cover Art",
            data=image_data,
        )
        self.audio.delall("APIC")
        self.audio.add(image)

    def modify_name(self, new_name: str):
        self.audio.delall("TIT2")
        self.audio.add(TIT2(encoding=3, text=new_name))
    
    def modify_track_artists(self, new_artists: list[str]):
        self.audio.delall("TPE1")
        self.audio.add(TPE1(encoding=3, text=new_artists))

    def modify_album_artists(self, new_artists: list[str]):
        self.audio.delall("TPE2")
        self.audio.add(TPE2(encoding=3, text=new_artists))
    
    def modify_album_name(self, new_name: str):
        self.audio.delall("TALB")
        self.audio.add(TALB(encoding=3, text=new_name))
    
    def modify_length(self, new_length: int):
        self.audio.delall("TLEN")
        self.audio.add(TLEN(encoding=3, text=str(new_length)))

    def save(self):
        self.audio.save()

    def print_metadata(self):
        self.audio.pprint()


if __name__ == "__main__":
    mp3_file_path = "downloads/echo-of-my-shadow.mp3"
    audio = AudioFile(mp3_file_path)
    metadata = SpotifyTrack(
        id="3GZ2pTgY1nXb8p0vl6j2e",
        name="Echo of My Shadow",
        trackArtists=["AURORA"],
        albumArtists=["AURORA"],
        albumName="Echo of My Shadow - Single",
        durationMs=215000,
        albumImageUrl="https://i.scdn.co/image/ab67616d0000b27338e85c163e5acd47e2b5e461"
    )

    audio.modify_name(metadata.name)
    audio.modify_track_artists(metadata.trackArtists)
    audio.modify_album_artists(metadata.albumArtists)
    audio.modify_album_name(metadata.albumName)
    audio.modify_length(metadata.durationMs)
    if metadata.albumImageUrl:
        audio.modify_art(metadata.albumImageUrl)
    audio.save()
