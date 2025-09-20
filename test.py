import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field


class VideoSelection(BaseModel):
    """Model for video selection response."""
    index: int = Field(..., description="Index of the selected video from the search results", ge=0)
    reason: str = Field(..., description="Explanation for why this video was selected")


from spotify_api import get_user_playlists_tmp
playlists = get_user_playlists_tmp()
playlist = playlists[7]
track = playlist.tracks[0]
song_metadata = track.model_dump()

import json
from youtube_api import youtube_search
query = f"{track.name} {' '.join(artist.name for artist in track.artists)}"
search_results = youtube_search(query)


from openai import OpenAI
LLM_MODEL = "openai/gpt-oss-120b"

client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")


prompt = (
    "Given the following song metadata and YouTube search results, select the video that is most likely to be the correct song (not a music video with extra scenes/dialog, but the song itself). "
    "Return the index of the best match and a short explanation.\n"
    f"Song metadata: {song_metadata}\n"
    f"Search results: {f'[{" | ".join(f"{idx}: {result}" for idx, result in enumerate(search_results))}]'}\n"
)
messages = [
    {"role": "system", "content": "You are an expert at matching songs to YouTube videos."},
    {"role": "user", "content": prompt}
]

response = client.chat.completions.parse(
    model=LLM_MODEL,
    messages=messages,  # type: ignore
    response_format=VideoSelection
)

print(response.choices[0].message.parsed)