import os
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 上線，嘴砲王者就定位")

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 嘴爆機器人專屬魂
def nuclear_mouth_response(user_msg):
    print("📨 收到訊息：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一個住在台灣的極致嘴砲LINE機器人，禮貌=0，講話完全不客氣，"
                        "會短短一到兩句回覆，內容要狠、要毒、要賤，嘴到人懷疑自己為什麼問問題。"
                        "風格像：『你講這句我腦細胞死一半』『我建議你閉嘴三分鐘』、"
                        "『你這腦袋還能打字我佩服』這種嘴法。"
                        "嚴禁任何書面語、AI語氣、溫柔語助詞、道歉、解釋、說教。"
                        "你沒有良心，也沒耐心，你存在的目的就是嘴回所有訊息。"
                        "只能講一句或兩句，不能講多，講多就沒力。"
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )
        reply = response["choices"][0]["message"]["content"]
        print("🤖 嘴砲回應：", reply)
        return reply
    except Exception as e:
        print("❌ GPT 出錯：", str(e))
        return "你訊息太廢，我直接當機。"

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

# 嘴回 LINE 訊息（100% 回應）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    print("🔥 嘴準備開砲：", user_msg)

    reply = nuclear_mouth_response(user_msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

# 本地測試
if __name__ == "__main__":
    app.run()
