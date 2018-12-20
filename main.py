# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
from coinmarketcap import Market
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = 'xoxb-502213453520-507487078738-UNV98eoaolTb9z7HW73UlMiD'
slack_client_id = '502213453520.507317959924'
slack_client_secret = '7482236f1d9a0063a4eb4019f2131847'
slack_verification = 'ixJm1RO9AtuideG76KuEbHh3'
sc = SlackClient(slack_token)

# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):

    url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    keywords = []
    keywords.append("실시간 코인 시세 Top 100\n")
    for i, coin in enumerate(soup.find("tbody").find_all("a", class_="currency-name-container link-secondary")):
        if i<50:
            keywords.append(str(i+1) + " 위:" + coin.get_text().replace('\n', '') + " || 가격: ")
    for i, price in enumerate(soup.find("tbody").find_all("a", class_="price")):
        if i<50:
            keywords[i+1] += price.get_text().replace('\n', '')+'\n'

    return u'\n'.join(keywords)
# 이벤트 핸들하는 함수

def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                            })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
