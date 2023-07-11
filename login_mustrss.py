from mastodon import Mastodon
from feedgen.feed import FeedGenerator
import os

# Register app - only once!
# You can replace 'your_app_name' and 'your_website' with your actual app name and website.
Mastodon.create_app(
     'mustrss',
     api_base_url = 'https://mastodon.social',
     to_file = 'clientcred.secret'
)

mastodon = Mastodon(
    client_id = 'clientcred.secret',
    api_base_url = 'https://mastodon.social'
)
# Replace 'your_email' and 'your_password' with your actual email and password.
mastodon.log_in(
    'email',
    'password',
    to_file = 'usercred.secret'
)