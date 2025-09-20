"""
llm_chat.py
Module for LLM chat completion using OpenAI SDK with OpenRouter as the model provider.
"""

import json
import os
import asyncio
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, Type, TypeVar
from dotenv import load_dotenv
load_dotenv()

# Pydantic models for structured responses
class YouTubeSearchQuery(BaseModel):
    """Model for YouTube search query response."""
    query: str = Field(..., description="The optimized YouTube search query")

class VideoSelection(BaseModel):
    """Model for video selection response."""
    index: int = Field(..., description="Index of the selected video from the search results", ge=0)

# You should set your OpenRouter API key as an environment variable: OPENROUTER_API_KEY

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "openai/gpt-oss-120b"

if not OPENROUTER_API_KEY:
    raise EnvironmentError("OPENROUTER_API_KEY environment variable not set.")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

# Type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)

async def chat_completion(messages: List[Dict[str, str]], response_model: Optional[Type[T]]) -> T:
    """
    Async: Get a chat completion from the LLM using OpenRouter as the provider.
    Args:
        messages (list): List of message dicts, e.g. [{"role": "user", "content": "Hello!"}]
        response_model (BaseModel, optional): Pydantic model for structured response
    Returns:
        str or BaseModel: The assistant's reply as string or parsed structured model
    """
    try:
        # Use structured output with JSON object
        response = client.chat.completions.parse(
            model=LLM_MODEL,
            messages=messages,  # type: ignore
            response_format=VideoSelection
        )
    except Exception as e:
        raise ValueError(f"LLM response parsing failed: {e}")
    # Parse and validate the response with Pydantic
    content = response.choices[0].message.parsed
    if content is None:
        raise ValueError("No content in LLM response")
    return content


    
async def generate_youtube_search_query(song_metadata):
    """
    Async: Given song metadata, generate a YouTube search query that is likely to find the song alone (not music videos with extra scenes/dialog).
    Args:
        song_metadata (dict): Should include keys like 'title', 'artist', 'album', 'year', etc.
    Returns:
        str: Search query string
    """
    prompt = (
        "Given the following song metadata, generate a YouTube search query that will find the song itself (not music videos with extra scenes or dialog). "
        "Prefer queries that target lyric videos, audio-only uploads, or reuploads by third-party channels. "
        f"Metadata: {song_metadata}\n"
        "Return the search query in the required format."
    )
    messages = [
        {"role": "system", "content": "You are an expert at crafting search queries for finding music on YouTube."},
        {"role": "user", "content": prompt}
    ]
    
    result = await chat_completion(messages, response_model=YouTubeSearchQuery)
    if isinstance(result, YouTubeSearchQuery):
        return result.query
    return ""

async def select_best_youtube_video(song_metadata, search_results):
    """
    Async: Given song metadata and a list of YouTube search results, select the best video that matches the song.
    Args:
        song_metadata (dict): Song info (title, artist, etc.)
        search_results (list): List of dicts, each with video metadata (title, channel, duration, etc.)
    Returns:
        dict: The selected video result (from search_results) with selection details
    """
    prompt = (
        "Given the following song metadata and YouTube search results, select the video that is most likely to be the correct song (not a music video with extra scenes/dialog, but the song itself). "
        "Return only the index of the best match.\n"
        f"Song metadata: {song_metadata}\n"
        "Search results:\n" +
        "\n".join([
            f"{idx}: Title: {result.get('title', 'N/A')}\n"
            f"   Channel: {result.get('channelTitle', 'N/A')}\n"
            f"   Published: {result.get('publishedAt', 'N/A')}\n"
            f"   Description: {result.get('description', 'N/A')[:100]}...\n"
            for idx, result in enumerate(search_results)
        ])
    )
    messages = [
        {"role": "system", "content": "You are an expert at matching songs to YouTube videos."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        result = await chat_completion(messages, response_model=VideoSelection)
        if isinstance(result, VideoSelection) and 0 <= result.index < len(search_results):
            return {"video": search_results[result.index]}
        else:
            return {"video": None, "error": f"LLM returned invalid index {getattr(result, 'index', None)}. Must be between 0 and {len(search_results)-1}."}
    except Exception as e:
        return {"video": None, "error": f"Failed to get valid selection from LLM: {e}"}


if __name__ == "__main__":
    # Example async usage
    async def main():
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, who won the world series in 2020?"}
        ]
        reply = await chat_completion(messages)
        print("Assistant:", reply)

    asyncio.run(main())


 # 'ConnectionError: {"object":"error","message":"[{\'type\': \'literal_error\', \'loc\': (\'body\', \'response_format\', \'type\'), \'msg\': \\"Input should be \'text\', \'json\', \'json_object\' or \'structural_tag\'\\", \'input\': \'json_schema\', \'ctx\': {\'expected\': \\"\'text\', \'json\', \'json_object\' or \'structural_tag\'\\"}}]","type":"BadRequestError","param":null,"code":400}'