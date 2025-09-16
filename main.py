from download_util import *

def main():
    url = input("Enter a youtube video URL: ")
    download_single_video(url=url, output_path="downloads", audio_only=True)


if __name__ == "__main__":
    main()
