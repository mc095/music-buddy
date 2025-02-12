import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_video(query):
    try:
        params = {
            "part": "snippet",
            "q": query,
            "key": YOUTUBE_API_KEY,
            "maxResults": 1,
            "type": "video",
            "videoCategoryId": 10  # Music category
        }

        response = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=params,
            timeout=10
        )
        data = response.json()

        if response.status_code != 200:
            return None

        if data.get("items"):
            return f"https://youtu.be/{data['items'][0]['id']['videoId']}"
        return None
    except Exception:
        return None
