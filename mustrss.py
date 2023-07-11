"""
   ^..^ CAT Soft - MustRSS - Mastodon RSS Personal Feed 
   for Skoda Infotainment System Online Services
   ------------------------ 
   11 July 2023 || glebone@gmail.com
   initially started on Blhodatne
"""

from feedgenerator import Rss201rev2Feed
from mastodon import Mastodon
import os


class EnclosureFeed(Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super(EnclosureFeed, self).add_item_elements(handler, item)
        handler.startElement("enclosure",
                                {u"url": item['enclosure_url'],
                                 u"type": "image/png"})
        handler.endElement("enclosure")

class MustFeedGen:
    def __init__(self):
        self.fg = EnclosureFeed(
            title = '^..^ Mastodon Skoda Feed',
            link = 'https://mastodon.social',
            description = 'Mastodon RSS Feed for Skoda infotainment system',
            language = 'en'
        )
        self.mastodon = Mastodon(access_token = 'usercred.secret', api_base_url = 'https://mastodon.social')


    def first_n_words(self, sentence, n):
        return ' '.join(sentence.split()[:n])


    def generate_feed(self):
        for toot in self.mastodon.timeline_home():
           print(toot)
           if toot['reblogged']:
               break
           if toot['sensitive']:
               break 
           item = {
                'title': toot['account']['display_name'] + " - "  +  self.first_n_words(toot['content'], 7),
                'link': toot['url'],
                'description': toot['content'],
                'pubdate': toot['created_at']}
           
           if 'media_attachments' in toot:
                item['enclosure_url'] = "https://seeklogo.com/images/S/skoda-logo-603B0DB338-seeklogo.com.png"
                for media in toot['media_attachments']:
                    item['enclosure_url'] = media['preview_url']
           else:
                item['enclosure_url'] = "https://seeklogo.com/images/S/skoda-logo-603B0DB338-seeklogo.com.png"
           
           self.fg.add_item(**item)

       
        xml = self.fg.writeString('utf-8') 
        
        with open('rss_feed.xml', 'w') as fp:
            fp.write(self.fg.writeString('utf-8'))

        with open('rss_feed.xml', 'r') as fp:
            print(fp.read())


from flask import Flask, Response
app = Flask(__name__)

@app.route('/rss')
def rss():
    mfg = MustFeedGen()
    mfg.generate_feed()
    with open('rss_feed.xml', 'r') as fp:
        data = fp.read()
    return Response(data, mimetype='text/xml')
