import requests
import os

def get_data():

    url = "https://openrouter.ai/api/v1/models"
    try:
        response = requests.get(url, timeout=20)
        data = response.json()['data']

        models = [{"id": m['id'], "ctx": m.get('context_length', 0)} for m in data]
        top_5 = sorted(models, key=lambda x: x['ctx'], reverse=True)[:10]
        return top_5
    except Exception as e:
        print(f"抓取失败: {e}")
        return None

def send_to_feishu(content):
    webhook_url = os.getenv("FEISHU_WEBHOOK")
    if not webhook_url:
        print("未配置飞书 Webhook")
        return

    payload = {
        "msg_type": "text",
        "content": {
            "text": f"🤖 大模型上下文窗口追踪\n----------------\n{content}"
        }
    }
    requests.post(webhook_url, json=payload)

if __name__ == "__main__":
    top_models = get_data()
    if top_models:
        msg_list = [f"排名 {i+1}: {m['id']} ({m['ctx']} tokens)" for i, m in enumerate(top_models)]
        send_to_feishu("\n".join(msg_list))
