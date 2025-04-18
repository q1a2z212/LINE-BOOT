import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 正在跑喔～")

# 顯示環境變數（你可以註解掉）
print("🔑 LINE_TOKEN:", os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
print("🔑 LINE_SECRET:", os.getenv('LINE_CHANNEL_SECRET'))
print("🔑 OPENAI_KEY:", os.getenv("OPENAI_API_KEY"))

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 幹話 GPT 回覆（台式風格 + 節流用）
def taiwanese_trash_talk(user_msg):
    print("📨 傳給 GPT 的內容：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個超像台灣人的 LINE 小助手，講話嘴砲、幽默、有點廢，偶爾裝懂，不要太認真。"},
                {"role": "user", "content": user_msg}
            ]
        )
        reply_text = response["choices"][0]["message"]["content"]
        print("🤖 GPT 說：", reply_text)
        return reply_text
    except Exception as e:
        print("❌ GPT 爆炸：", str(e))
        return "欸好像有點當機，你再說一次啦～"

# Webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("👂 收到訊息：", user_msg)

    # ➤ 控制回覆機率（20%）
    if random.random() > 0.2:
        print("😴 這輪跳過，先裝死一下")
        return

    reply = taiwanese_trash_talk(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 本地開發用
if __name__ == "__main__":
    app.run()
