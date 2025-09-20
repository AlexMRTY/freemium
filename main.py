from download_util import *
from llm_chat import select_best_youtube_video
from spotify_api import SpotifyApi
from youtube_api import *
from id3_utils import *
import pprint
import json
import asyncio

def download_video():
    query = input("Enter a search query: ")
    search_results = youtube_search(query)
    for idx, result in enumerate(search_results):
        print(f"[{idx}] Title: {result.title}, Video ID: {result.videoId}")

    chosen_video = input("Choose a video: ")
    if chosen_video.isdigit() and 0 <= int(chosen_video) < len(search_results):
        video_id = search_results[int(chosen_video)].videoId
        print(f"Downloading video ID: {video_id}")
        download_single_video(f"https://www.youtube.com/watch?v={video_id}", output_path="downloads", audio_only=True)
    else:
        print("Invalid choice.")



async def main():
    from spotify_api import get_user_playlists_tmp
    playlists = get_user_playlists_tmp()
    for idx, playlist in enumerate(playlists):
        print(f"[{idx}] {playlist.name} (ID: {playlist.id}) - {len(playlist.tracks)} tracks")

    chosen_playlist = 7
    # if chosen_playlist.isdigit() and 0 <= int(chosen_playlist) < len(playlists):
    playlist = playlists[chosen_playlist]
    print(f"Downloading playlist: {playlist.name} with {len(playlist.tracks)} tracks")
    for track in playlist.tracks:
        query = f"{track.name} {' '.join(artist.name for artist in track.artists)}"
        print(f"Searching for: {query}")
        search_results = youtube_search(query)
        if search_results:
            # Use model_dump instead of dict for Pydantic v2+
            best_video = await select_best_youtube_video(track.model_dump(), search_results)
            if best_video and best_video['video']:
                print(f"Downloading: {best_video['video']}")
                output_file = download_single_video(f"https://www.youtube.com/watch?v={best_video['video'].videoId}", output_path=f"downloads/{track.album.name}", file_name=track.name, audio_only=True)
                if output_file["success"] == True:
                    audio = AudioFile(f"downloads/{track.album.name}/{track.name}.mp3")
                    audio.modify_metadata(track)
            else:
                print(f"No suitable video found for: {query} Reason: {best_video.get('reason') if best_video else 'Unknown error'}")
        else:
            print(f"No YouTube results found for: {query}")

if __name__ == "__main__":
    asyncio.run(main())
