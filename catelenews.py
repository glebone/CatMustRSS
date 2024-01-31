import json
from telethon import TelegramClient, events

# Load your channels
with open('channels.json', 'r') as file:
    channels = json.load(file)["channels"]

print(channels)

# Telegram client setup
api_id = ''  # Replace with your API ID
api_hash = ''  # Replace with your API Hash
client = TelegramClient('session_name', api_id, api_hash)

async def get_latest_posts(channel_name, limit=10):
    async with client:
        channel = await client.get_entity(channel_name)
        posts = await client.get_messages(channel, limit=limit)
        return posts

# Example usage
async def main():
    for channel in channels:
        posts = await get_latest_posts(channel, 5)  # Get 5 latest posts
        print(f"Latest posts in {channel}:")
        for post in posts:
            print(post.text)

with client:
    client.loop.run_until_complete(main())
