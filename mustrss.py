"""
   ^..^ CAT Soft - MastRSS - Mastodon RSS Personal Feed 
   for Skoda Infotainment System Online Services
   ------------------------ 
   11 July 2023 || glebone@gmail.com
   initially started on Blhodatne
"""

from feedgenerator import Rss201rev2Feed
from mastodon import Mastodon
import os
import requests
from bs4 import BeautifulSoup
from newspaper import Article



class EnclosureFeed(Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super(EnclosureFeed, self).add_item_elements(handler, item)
        handler.startElement("enclosure",
                                {u"url": item['enclosure_url'],
                                 u"type": "image/png"})
        handler.endElement("enclosure")


class MastFeedGen:
    def __init__(self):
        self.fg = EnclosureFeed(
            image='https://seeklogo.com/images/S/skoda-logo-603B0DB338-seeklogo.com.png',
            title = '^..^ Mastodon Skoda Feed',
            link = 'https://mastodon.social',
            description = 'Mastodon RSS Feed for Skoda infotainment system',
            language = 'en'
        )
        self.mastodon = Mastodon(access_token = 'usercred.secret', api_base_url = 'https://mastodon.social')


    def first_n_words(self, sentence, n):
        if sentence.startswith('<p>'):
            sentence = sentence[3:]
        return ' '.join(sentence.split()[:n])


    def fetch_article_content(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8' 
        article = Article('')
        article.set_html(response.text)
        article.parse()
        return article.text
    
    def content_fetcher(self, content):
        exclude_words = ['tags', 'statuses', 'mastodon']
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a')
        print("-----------------")
        article = ""
        for link in links:
            url = link.get('href')
            if not any(word in url for word in exclude_words):
                print(f"Toot  contains a link: {url}")
                try:
                    article = self.fetch_article_content(url)
                    print(f"The main text of the article at {url} is: \n\n{article}\n")
                except Exception as e:
                    print(f"Failed to fetch article from {url} due to error: {e}")
                break
        print(article)
        return article        
        
    def generate_feed(self):
        for toot in self.mastodon.timeline_home():
           #print(toot)
           cur_toot = toot
           if toot['sensitive']:
               continue
           if toot['reblog'] != None:
                cur_toot = toot['reblog']
           
           item = {
                'title': cur_toot['account']['display_name'][:5] + " - "  +  self.first_n_words(cur_toot['content'], 12),
                'link': cur_toot['url'],
                'pubdate': cur_toot['created_at']}
           
           if self.content_fetcher(cur_toot['content']) != "":
                item['description'] = self.content_fetcher(cur_toot['content'])
           else:
                item['description'] = cur_toot['content']

           if 'media_attachments' in cur_toot:
                item['enclosure_url'] = "https://seeklogo.com/images/S/skoda-logo-603B0DB338-seeklogo.com.png"
                for media in cur_toot['media_attachments']:
                    if 'preview' in media and 'small' in media['preview']:
                        item['enclosure_url'] = media['preview']['small']
                    else:
                        item['enclosure_url'] = media['preview_url']
           else:
                item['enclosure_url'] = "https://seeklogo.com/images/S/skoda-logo-603B0DB338-seeklogo.com.png"
           
           self.fg.add_item(**item)

       
        xml = self.fg.writeString('utf-8') 
        
        with open('rss_feed.xml', 'w') as fp:
            fp.write(self.fg.writeString('utf-8'))


        #with open('rss_feed.xml', 'r') as fp:
            #print(fp.read())


from flask import Flask, Response
app = Flask(__name__)

@app.route('/rss')
def rss():
    mfg = MastFeedGen()
    mfg.generate_feed()
    with open('rss_feed.xml', 'r') as fp:
        data = fp.read()
    return Response(data, mimetype='text/xml')
