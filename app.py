import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 準備好了，極簡嘴砲模式啟動")

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 嘴砲型 GPT 回覆（極短版）
def lazy_short_response(user_msg):
    print("📨 傳送內容給 GPT：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一個住台灣的嘴砲朋友，講話只講一句話、短短的，"
                        "像LINE群組那種回一兩句就閉嘴的嘴砲王。"
                        "語氣可以鬧、裝死、冷笑話、嗆人、懶懶的，但一定要短。"
                        "回覆時避免長篇大論、說教或過度說明，"
                        "像『蛤？你問我？』『我知道個鬼啦』『你要我負責？笑死』這種風格。"
                        "不準用書面語、不能太認真，也不能看起來像AI。"
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        print("🤖 回應：", reply)
        return reply
    except Exception as e:
        print("❌ GPT 錯誤：", str(e))
        return "欸剛剛斷線，我再裝死一次"

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

# 接收 LINE 訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("👂 收到訊息：", user_msg)

    # 超省話機率，只回 10%
    if random.random() > 0.1:
        print("😶 裝死模式啟動")
        return

    reply = lazy_short_response(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 本地測試用
if __name__ == "__main__":
    app.run()
