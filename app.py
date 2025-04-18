import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 正在開嘴運作中")

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 嘴砲台味回覆系統
def taiwanese_lazy_chat(user_msg):
    print("📨 傳給 GPT 的訊息：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一個講話超台的朋友，平常很懶但又會突然爆講幹話，"
                        "你會用表情符號，講話像台灣人，會說『不然勒』『你問這幹嘛啦』、"
                        "『先喝個奶茶冷靜一下』，有時候突然認真一下但不要太長，"
                        "整體講話要像 LINE 廢話王，不要太知識型，越像朋友越好。"
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        print("🤖 GPT 回應：", reply)
        return reply
    except Exception as e:
        print("❌ GPT 出錯：", str(e))
        return "欸我剛剛 lag 了一下，再說一次啦 😵"

# LINE webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 使用者傳文字訊息時觸發
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("👂 使用者說：", user_msg)

    # 懶人設定：只回 20% 的訊息
    if random.random() > 0.2:
        print("😴 太懶了這輪不回")
        return

    reply = taiwanese_lazy_chat(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 本地用
if __name__ == "__main__":
    app.run()
