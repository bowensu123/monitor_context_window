import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
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


def send_email(content):
    # 从 GitHub Secrets 读取配置
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("RECEIVER_EMAIL")
    

    if not all([sender, password, receiver]):
        print("邮件配置不完整，跳过发送")
        return


    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = Header("🤖 大模型上下文窗口监控报表", 'utf-8')

    try:
        # 如果是 163 邮箱，改为 smtp.163.com
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, [receiver], message.as_string())
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {e}")

if __name__ == "__main__":
    top_models = get_data()
    if top_models:
        msg_content = "\n".join([f"排名 {i+1}: {m['id']} ({m['ctx']} tokens)" for i, m in enumerate(top_models)])
        
        # 同时发送到飞书和邮件
        send_to_feishu(msg_content)
        send_email(msg_content)
