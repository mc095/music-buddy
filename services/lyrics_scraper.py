import requests
from bs4 import BeautifulSoup, Comment

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_lyrics(song_name):
    try:
        # Step 1: Search for the song
        search_url = f"https://search.azlyrics.com/search.php?q={requests.utils.quote(song_name)}"
        search_response = requests.get(search_url, headers=HEADERS, timeout=10)
        
        if search_response.status_code != 200:
            return "🔍 Lyrics search failed. Try again later!"
            
        # Step 2: Find lyrics page URL
        soup = BeautifulSoup(search_response.text, "html.parser")
        results_table = soup.find("table", class_="table")
        if not results_table:
            return "❌ No lyrics found for this song"
            
        lyrics_path = results_table.find("a", href=True)["href"]
        
        # Step 3: Fetch and parse lyrics
        lyrics_response = requests.get(lyrics_path, headers=HEADERS, timeout=10)
        lyrics_soup = BeautifulSoup(lyrics_response.text, "html.parser")
        
        # Find lyrics using comment marker
        target_comment = lyrics_soup.find(string=lambda text: isinstance(text, Comment) and "Usage of azlyrics.com" in text)
        if not target_comment:
            return "❌ Couldn't parse lyrics page"
            
        lyrics_div = target_comment.find_next("div")
        return f"🎵 Lyrics:\n{lyrics_div.get_text(strip=True, separator='\n')[:1000]}..."
    except Exception as e:
        return f"⚠️ Error fetching lyrics: {str(e)}"