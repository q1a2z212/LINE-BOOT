import os
import openai
import random
import time
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ 嘴砲模式啟動中")

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 嘴砲內容庫
savage_lines = [
    "你這句話笑得我 CPU 當機。",
    "我不想嘴，但你真的好嘴。",
    "你這 IQ 敢講話，我都佩服。",
    "你有閒喔？不如去反省一下。",
    "講這句你不臉紅？",
    "這話我 AI 看了都想關機。",
    "你那個腦回路是 WiFi 不穩嗎？"
]

# 判斷這句話值不值得嘴
def is_worth_roasting(user_msg):
    keywords = ["笑", "哭", "餓", "煩", "累", "無聊", "？", "0.0", "唉", "幹", "靠"]
    return any(k in user_msg for k in keywords) and random.random() < 0.5  # 50% 嘴

# 嘴砲機制（直接用固定句子，也可改 GPT）
def generate_bot_reply(user_msg):
    return random.choice(savage_lines)

# 接收訊息與回覆邏輯
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    print("👤 使用者說：", user_msg)

    if not is_worth_roasting(user_msg):
        print("🤫 機器人選擇裝死不回應")
        return  # 裝死，不回覆

    delay = random.randint(1, 5)
    print(f"⏳ 延遲回應 {delay} 秒中...")
    time.sleep(delay)

    reply = generate_bot_reply(user_msg)
    print("💬 機器人回：", reply)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

if __name__ == "__main__":
    app.run()
