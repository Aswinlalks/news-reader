import requests
import xml.etree.ElementTree as ET
import json
import os

# Live Kochi 365 Channel ID
CHANNEL_ID = "UCCf2h8k0MmeB9qo8XG62kiA"
RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"

def get_latest_video():
    """Fetches the most recent video from the YouTube RSS feed."""
    try:
        response = requests.get(RSS_URL)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # Read YouTube's XML structure
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'media': 'http://search.yahoo.com/mrss/'}
        entry = root.find('atom:entry', ns)
        
        if not entry:
            return None
            
        title = entry.find('atom:title', ns).text
        link = entry.find('atom:link', ns).attrib['href']
        
        media_group = entry.find('media:group', ns)
        description = media_group.find('media:description', ns).text if media_group is not None else "No description provided."
        
        return {"title": title, "link": link, "description": description}
    except Exception as e:
        print(f"Error fetching YouTube feed: {e}")
        return None

def main():
    print("Checking for new videos...")
    video = get_latest_video()
    
    if not video:
        print("No videos found or failed to fetch.")
        return
        
    print(f"Latest video found: {video['title']}")
    
    news_list = []
    # Open the existing news database if it exists
    if os.path.exists("news.json"):
        with open("news.json", "r", encoding="utf-8") as f:
            try:
                news_list = json.load(f)
            except json.JSONDecodeError:
                pass
                
    # Check if this video is already in our database
    if news_list and news_list[0].get('video_link') == video['link']:
        print("This video has already been processed and added to the website.")
        return

    print("New video detected! Adding to website...")
    
    # We replace line breaks (\n) with HTML breaks (<br>) so the description formats nicely on your site
    formatted_description = video['description'].replace('\n', '<br>')
    
    new_article = {
        "title": video['title'],
        "content": formatted_description,
        "video_link": video['link']
    }
    
    # Add new article to the top of the list
    news_list.insert(0, new_article)
    # Keep the site fast by only holding the 10 newest articles
    news_list = news_list[:10] 
    
    # Save the updated list back to the JSON file
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)
        
    print("Successfully added new video to news.json!")

if __name__ == "__main__":
    main()