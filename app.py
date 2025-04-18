import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 上線中，懶到只回十分之一")

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 嘴砲風格 GPT 回應
def lazy_taiwanese_response(user_msg):
    print("📨 傳送內容給 GPT：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位講話嘴砲、住在台灣的朋友，講話不能太認真，"
                        "有點賤但不失禮，會說『靠北喔』『你問這幹嘛啦』『我怎麼知道啦哈哈』，"
                        "講話像LINE群組裡的嘴砲王，有時候裝死、有時候丟冷笑話、"
                        "講話自然、鬆、短，不要用書面語或客套話。"
                        "完全不要說『您好』或『我是 AI』這種鬼話。"
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        print("🤖 GPT 回應：", reply)
        return reply
    except Exception as e:
        print("❌ GPT 爆炸了：", str(e))
        return "我剛剛去喝奶茶了，沒聽清楚啦😴"

# Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 使用者傳訊息觸發
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("👂 收到訊息：", user_msg)

    # 懶人版設定：只回 10% 的訊息
    if random.random() > 0.1:
        print("😶 我裝死，這輪不嘴（省錢模式）")
        return

    reply = lazy_taiwanese_response(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 本地測試用
if __name__ == "__main__":
    app.run()
