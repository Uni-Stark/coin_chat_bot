from slacker import Slacker

slack = Slacker('xoxb-502213453520-507487078738-UNV98eoaolTb9z7HW73UlMiD')

# Send a message to #general channel
slack.chat.post_message('#general', 'Hello fellow slackers!')

# Get users list
response = slack.users.list()
users = response.body['members']

# Upload a file
slack.files.upload('hello.txt')

# If you need to proxy the requests
proxy_endpoint = 'http://127.0.0.1:4040'
slack = Slacker('xoxb-502213453520-507487078738-UNV98eoaolTb9z7HW73UlMiD',
                http_proxy=proxy_endpoint,
                https_proxy=proxy_endpoint)

# Advanced: Use `request.Session` for connection pooling (reuse)
from requests.sessions import Session
with Session() as session:
    slack = Slacker(token, session=session)
    slack.chat.post_message('#general', 'All these requests')
    slack.chat.post_message('#general', 'go through')
    slack.chat.post_message('#general', 'a single https connection')
