import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import random

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

keyword_responses = {
    "累": {
        "text": "累了嗎？先躺平一下，但別忘了起來喔～",
        "image": "https://i.imgur.com/你的梗圖.jpg"
    },
    "餓": {
        "text": "又餓了？吃圖補一下元氣吧！",
        "image": "https://i.imgur.com/你的梗圖.jpg"
    }
}

default_responses = [
    "這句話我聽不懂，反正你開心就好～",
    "人類語言博大精深啊！"
]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    for keyword, response in keyword_responses.items():
        if keyword in user_msg:
            messages = [
                TextSendMessage(text=response["text"]),
                ImageSendMessage(original_content_url=response["image"],
                                 preview_image_url=response["image"])
            ]
            line_bot_api.reply_message(event.reply_token, messages)
            return
    random_reply = random.choice(default_responses)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=random_reply))

if __name__ == "__main__":
    app.run()
