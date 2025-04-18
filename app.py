import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 正在運作！")

# 顯示環境變數（開發用，可刪除）
print("🔑 LINE_TOKEN：", os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
print("🔑 LINE_SECRET：", os.getenv('LINE_CHANNEL_SECRET'))
print("🔑 OPENAI_KEY：", os.getenv("OPENAI_API_KEY"))

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 純 GPT 文字回覆，不附圖、不貼連結
def ai_funny_response(user_msg):
    print("📨 傳給 GPT 的內容：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個有點嘴砲但很暖的 LINE AI，小小吐槽使用者、回應幹話風格，但不能兇也不能罵人。"},
                {"role": "user", "content": user_msg}
            ]
        )
        reply_text = response["choices"][0]["message"]["content"]
        print("🤖 GPT 回覆：", reply_text)
        return reply_text
    except Exception as e:
        print("❌ GPT 發生錯誤：", str(e))
        return "我剛剛不小心睡著了，再問一次好嗎？😴"

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

# 處理 LINE 訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("📥 使用者訊息：", user_msg)

    # 只有 30% 機率回應（避免吵死人）
    if random.random() > 0.3:
        print("🤫 這次選擇靜靜不說話")
        return

    reply_text = ai_funny_response(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# 本地測試用（Render 不會執行這段）
if __name__ == "__main__":
    app.run()
