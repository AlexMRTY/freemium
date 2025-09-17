
# youtube-api.py: Module for YouTube API key access
# Loads API_KEY from .env using python-dotenv


import os
from typing import List
from dotenv import load_dotenv
import googleapiclient.discovery
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

def get_api_key():
    """Get API key from .env file."""
    return os.getenv('YOUTUBE_API_KEY')


class YouTubeSearchResult(BaseModel):
    title: str
    videoId: str
    channelTitle: str
    publishedAt: str
    description: str

def youtube_search(query: str, max_results: int = 5) -> List[YouTubeSearchResult]:
    """
    Searches YouTube for videos based on a query.

    Args:
        query: The search term.
        max_results: The maximum number of results to return (default is 5).

    Returns:
        A list of dictionaries, where each dictionary represents a search result
        and contains 'title', 'videoId', and 'channelTitle'.
        Returns an empty list if no results are found or an error occurs.

        Example:
        [
          {
              "title":"AURORA - Echo of My Shadow (Visualiser)",
              "videoId":"5TLG3gU--qw",
              "channelTitle":"iamAURORAVEVO",
              "publishedAt":"2024-06-07T08:04:14Z",
              "description":"Music video by AURORA performing Echo of My Shadow (Visualiser).© 2024 Universal Music Operations Limited."
          },
        ]
    """
    try:
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=get_api_key())

        request = youtube.search().list(
            part="snippet",
            q=query,
            maxResults=max_results,
            type="video"
        )
        response = request.execute()

        search_results: List[YouTubeSearchResult] = []
        for item in response.get("items", []):
            search_results.append(YouTubeSearchResult(
                title=item["snippet"]["title"],
                videoId=item["id"]["videoId"],
                channelTitle=item["snippet"]["channelTitle"],
                publishedAt=item["snippet"]["publishedAt"],
                description=item["snippet"]["description"]
            ))

        return search_results

    except Exception as e:
        print(f"An error occurred: {e}")
        return []



