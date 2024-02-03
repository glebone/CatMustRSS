import json
from telethon import TelegramClient
from feedgenerator import Rss201rev2Feed
from datetime import datetime

class TelegramFeedGen:
    def __init__(self, api_id, api_hash, channel_file='channels.json', output_format='json'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.channels = self.load_channels(channel_file)
        self.output_format = output_format

    def load_channels(self, channel_file):
        with open(channel_file, 'r') as file:
            channels = json.load(file)["channels"]
        return channels

    async def get_latest_posts(self, channel_name, limit=10):
        async with self.client:
            channel = await self.client.get_entity(channel_name)
            posts = await self.client.get_messages(channel, limit=limit)
            formatted_posts = []
            for post in posts:
                images = []
                if post.media:
                    if hasattr(post.media, 'photo'):  # For MessageMediaPhoto
                        # Ideally, use something like post.media.photo.file_reference
                        images.append("Placeholder for image URL")
                    elif hasattr(post.media, 'document'):  # For MessageMediaDocument (could be images/documents)
                        # Checking if it's an image
                        images.append("Placeholder for document URL")
                # Note: The placeholders above should be replaced with actual logic to fetch image URLs

                post_data = {
                    'text': post.message if post.message else '',
                    'date': post.date.isoformat(),
                    'author': post.sender_id,
                    'images': images
                }
                formatted_posts.append(post_data)
            return formatted_posts

    def to_json(self, posts):
        # ensure_ascii=False to properly display Unicode characters
        return json.dumps(posts, ensure_ascii=False)

    def to_rss(self, posts, channel_name):
        feed = Rss201rev2Feed(
            title=f"{channel_name} Telegram Channel Feed",
            link=f"https://t.me/{channel_name}",
            description=f"Latest posts from {channel_name}",
            language="en",
        )
        for post in posts:
            # Including images directly in the description with HTML <img> tags
            description_with_images = post['text'] + ''.join([f"<img src='{image}'/>" for image in post['images']])
            feed.add_item(
                title=f"Post on {post['date']}",
                link=f"https://t.me/{channel_name}",
                description=description_with_images,
                pubdate=datetime.fromisoformat(post['date'])
            )
        return feed.writeString('utf-8')

    async def fetch_posts(self):
        all_posts = []  # Create an empty list to collect posts from all channels
        for channel in self.channels:
            print(f"Fetching posts for {channel}")
            print("=================================")
            posts = await self.get_latest_posts(channel, 5)  # Get 5 latest posts
            formatted_posts = json.dumps(posts, ensure_ascii=False)  # Handle Unicode
            if self.output_format == 'json':
               all_posts.append(formatted_posts)  # Append posts to the list
            elif self.output_format == 'rss':
                rss_output = self.to_rss(posts, channel)
                all_posts.append(rss_output)  # Append RSS output to the list

        return all_posts  # Return the list containing posts from all channels


# Example usage
if __name__ == "__main__":
    # Replace with your actual API ID and Hash
    api_id = ''
    api_hash = ''
    output_format = 'json'  # Can be 'json' or 'rss'

    tg_feed_gen = TelegramFeedGen(api_id, api_hash, output_format=output_format)
    with tg_feed_gen.client:
        tg_feed_gen.client.loop.run_until_complete(tg_feed_gen.fetch_posts())
