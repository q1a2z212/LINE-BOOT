import os
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

# 初始化 Flask
app = Flask(__name__)

# 初始化 LINE BOT
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 初始化 OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI 回覆 + 梗圖 判斷
def ai_response_with_meme(user_msg):
    # 送出聊天內容給 GPT
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一個幽默的 AI 助理，會用簡短幹話回應並懂得丟梗圖。"},
            {"role": "user", "content": user_msg}
        ]
    )

    reply_text = response["choices"][0]["message"]["content"]

    # 梗圖邏輯（你可以自己加更多條件！）
    meme = None
    if "餓" in user_msg or "吃" in reply_text:
        meme = "https://i.imgur.com/6hDFYxD.jpg"  # 換成你自己的梗圖連結
    elif "累" in user_msg or "休息" in reply_text:
        meme = "https://i.imgur.com/XOW5ehK.jpg"
    elif "哭" in user_msg or "難過" in reply_text:
        meme = "https://i.imgur.com/rEYhX2D.jpg"

    return reply_text, meme

# LINE Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 使用者訊息處理（這段只要保留一次就好！）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    reply_text, meme_url = ai_response_with_meme(user_msg)

    messages = [TextSendMessage(text=reply_text)]
    if meme_url:
        messages.append(ImageSendMessage(
            original_content_url=meme_url,
            preview_image_url=meme_url
        ))

    line_bot_api.reply_message(event.reply_token, messages)

# Render 不會用這段，但保留給本地測試
if __name__ == "__main__":
    app.run()
