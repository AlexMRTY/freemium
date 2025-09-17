from download_util import *
from youtube_api import *
from id3_utils import *
import pprint

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

    

def main():
    download_video()


if __name__ == "__main__":
    main()
