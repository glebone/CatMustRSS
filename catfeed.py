from flask import Flask, Response
from quart import Quart, jsonify
import telegramfeedgen
import json

app = Flask(__name__)
quart_app = Quart(__name__)


api_id = ''
api_hash = ''



@app.route('/')
def hello_flask():
    return "Hello, Flask!"

@quart_app.route('/asgi')
async def hello_asgi():
    return "Hello, ASGI!"

@quart_app.route('/telefeed', methods=['GET'])
async def get_telefeed_json():
    output_format = 'json'

    tg_feed_gen = telegramfeedgen.TelegramFeedGen(api_id, api_hash, output_format=output_format)
    async with tg_feed_gen.client:  # Use async with
        posts = await tg_feed_gen.fetch_posts()
        return Response(posts, mimetype='application/json; charset=utf-8')
    

@quart_app.route('/telefeedrss', methods=['GET'])
async def get_telefeed_rss():
    output_format = 'rss'

    tg_feed_gen = telegramfeedgen.TelegramFeedGen(api_id, api_hash, output_format=output_format)
    async with tg_feed_gen.client:  # Use async with
        posts = await tg_feed_gen.fetch_posts()
        return Response(posts, content_type='application/rss+xml; charset=utf-8')


if __name__ == '__main__':
    import hypercorn
    hypercorn.asyncio.run(hypercorn.Config.from_mapping(
        bind=["0.0.0.0:8000"], app="app:quart_app"))
