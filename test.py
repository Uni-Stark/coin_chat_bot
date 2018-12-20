import json
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = 'xoxb-502213453520-507487078738-pspACr4G8UxxoMoQ8KOc1jco'
slack_client_id = '502213453520.507317959924'
slack_client_secret = '7482236f1d9a0063a4eb4019f2131847'
slack_verification = 'ixJm1RO9AtuideG76KuEbHh3'
sc = SlackClient(slack_token)


def _crawl_coin_currency(text):
    url = "https://www.coinmarketcap.com/ko"

# URL 주소에 있는 HTML 코드를 soup에 저장합니다.
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")

    cur = []
    cur.append("실시간 코인 시세 Top 10\n")
    for i, coin in enumerate(soup.find("tbody").find_all("a", class_="currency-name-container link-secondary")):
        if i < 10:
            cur.append(str(i+1) + " 위:" + coin.get_text().replace('\n', '') + " || 가격: ")
    for i, price in enumerate(soup.find("tbody").find_all("a", class_="price")):
        if i < 10:
            cur[i+1] += price.get_text().replace('\n', '')+ '\n'

    return u'\n'.join(cur)

def _get_coin_currency(text):
    url = "https://www.coinmarketcap.com/ko"
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    name = []

    for i, coin in enumerate(soup.find("tbody").find_all("a", class_="currency-name-container link-secondary")):
        if coin is text:
            name.append(coin.get_text().replace('\n', ''))


                    # else:
                        # price[i+1] += j.get_text().replace('\n', '')
            # else:
            #     name.coin.get_text().replace('\n', '')
            #     for j in coin.find("a",class_="price"):
            #         if price is None:
            #             price.append(j.get_text().replace('\n',''))
            #         else:
            #             price[i+1] += j.get_text().replace('\n', '')
    for i , price in enumerate(soup.find("tbody").find_all("a", class_="price")):
        if i < 10:
            price.append(coin.get_text().replace('\n', ''))
    result = dict(zip([coin_name for coin_name in name], [coin_price for coin_price in price]))



    final_result = result[text]
    return final_result


def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        if '코인' in text:
            keywords = _crawl_coin_currency(text)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )
        else :
            keywords = _get_coin_currency(text)
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )
        return make_response("App mention message has been sent", 200,)

    message = "You have not added an event handler for the %s" % event_type

    return make_response(message, 200, {"X-Slack-No_Retry": 1})

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

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000)
