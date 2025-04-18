import os
import random
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

print("✅ app.py 正在運作！")

# 環境變數確認（開發用，可刪）
print("🔑 LINE_TOKEN：", os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
print("🔑 LINE_SECRET：", os.getenv('LINE_CHANNEL_SECRET'))
print("🔑 OPENAI_KEY：", os.getenv("OPENAI_API_KEY"))

# 初始化
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))
openai.api_key = os.getenv("OPENAI_API_KEY")

# 單純 GPT 回應（不附圖不連結）
def ai_funny_response(user_msg):
    print("📨 傳給 GPT 的內容：", user_msg)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一個有點嘴砲但很暖的 LINE AI，小小吐槽使用者、回應幹話風格，但不能兇也不能罵人。"},
                {"role": "user", "content": user_msg}
