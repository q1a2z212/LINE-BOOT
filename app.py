import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

print("✅ app.py 正在運作！")

# 顯示環境變數確認
print("🔑 LINE_TOKEN：", os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
print("🔑 LINE_SECRET：", os.getenv('LINE_CHANNEL_SECRET'))
print("🔑 OPENAI_KEY：", os.getenv("OPENAI_API_KEY"))

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI 回應 + 梗圖邏輯
def ai_response_with_meme(user_msg):
    print("📨 傳給 GPT 的內容：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個幽默的 AI 助理，會用簡短幹話回應並懂得丟梗圖。"},
                {"role": "user", "content": user_msg}
            ]
        )
        print("✅ GPT 回傳：", response)
        reply_text = response["choices"][0]["message"]["content"]

        meme = None
        if "餓" in user_msg or "吃" in reply_text:
            meme = "https://i.imgur.com/M4fE60O.jpeg"
        elif "累" in user_msg or "休息" in reply_text:
            meme = "https://i.imgur.com/Cer9NQo.jpeg"
        elif "哭" in user_msg or "難過" in reply_text:
            meme = "https://i.imgur.com/8dVDjBO.jpeg"

        return reply_text, meme

    except Exception as e:
        print("❌ GPT 發生錯誤：", str(e))
        return "AI 壞掉了，等它重啟中... 😵‍💫", None

# LINE callback 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("📥 使用者訊息：", user_msg)

    # 只有 30% 機率回覆
    if random.random() > 0.3:
        print("🫥 這次安靜不回應")
        return

    reply_text, meme_url = ai_response_with_meme(user_msg)
    print("🤖 GPT 回覆：", reply_text)
    print("🖼️ 梗圖連結：", meme_url)

    messages = [TextSendMessage(text=reply_text)]
    if meme_url:
        messages.append(ImageSendMessage(
            original_content_url=meme_url,
            preview_image_url=meme_url
        ))

    line_bot_api.reply_message(event.reply_token, messages)

# 本地測試用
if __name__ == "__main__":
    app.run()
