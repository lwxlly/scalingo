import os
import json
import base64
import re
import requests
from flask import Flask, Response

# ------------------ 配置 ------------------
UPLOAD_URL = os.environ.get('UPLOAD_URL', '')
PROJECT_URL = os.environ.get('PROJECT_URL', '')
AUTO_ACCESS = os.environ.get('AUTO_ACCESS', 'false').lower() == 'true'
FILE_PATH = os.environ.get('FILE_PATH', './.cache')
SUB_PATH = os.environ.get('SUB_PATH', 'sub')
UUID = os.environ.get('UUID', 'e4abfe17-2934-483b-a072-08bbcd6bd60c')
NAME = os.environ.get('NAME', 'Vls')
CHAT_ID = os.environ.get('CHAT_ID', '6048840573')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8006056537:AAHFCK3fz1ktbS9XFa9LODCD6gnuFypOwqg')
CFIP = os.environ.get('CFIP', 'www.visa.com.tw')
CFPORT = int(os.environ.get('CFPORT', '443'))

sub_path = os.path.join(FILE_PATH, 'sub.txt')
list_path = os.path.join(FILE_PATH, 'list.txt')

# ------------------ 初始化目录 ------------------
if not os.path.exists(FILE_PATH):
    os.makedirs(FILE_PATH)

# ------------------ Flask ------------------
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World', 200

@app.route(f'/{SUB_PATH}')
def get_sub():
    if os.path.exists(sub_path):
        with open(sub_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    else:
        return 'Not Found', 404

# ------------------ 节点生成 ------------------
def generate_links():
    ISP = "LocalISP"
    argo_domain = CFIP
    VMESS = {
        "v": "2",
        "ps": f"{NAME}-{ISP}",
        "add": CFIP,
        "port": CFPORT,
        "id": UUID,
        "aid": "0",
        "scy": "none",
        "net": "ws",
        "type": "none",
        "host": argo_domain,
        "path": "/vmess-argo?ed=2560",
        "tls": "tls",
        "sni": argo_domain,
        "fp": "chrome"
    }

    list_txt = f"""
vless://{UUID}@{CFIP}:{CFPORT}?encryption=none&security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Fvless-argo%3Fed%3D2560#{NAME}-{ISP}

vmess://{base64.b64encode(json.dumps(VMESS).encode()).decode()}

trojan://{UUID}@{CFIP}:{CFPORT}?security=tls&sni={argo_domain}&fp=chrome&type=ws&host={argo_domain}&path=%2Ftrojan-argo%3Fed%3D2560#{NAME}-{ISP}
"""

    with open(list_path, 'w', encoding='utf-8') as f:
        f.write(list_txt)

    sub_txt = base64.b64encode(list_txt.encode()).decode()
    with open(sub_path, 'w', encoding='utf-8') as f:
        f.write(sub_txt)

    # Telegram 推送
    if BOT_TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        escaped_name = re.sub(r'([_*\[\]()~>#+=|{}.!\-])', r'\\\1', NAME)
        params = {
            "chat_id": CHAT_ID,
            "text": f"**{escaped_name}节点推送通知**\n{sub_txt}",
            "parse_mode": "MarkdownV2"
        }
        try:
            requests.post(url, params=params)
            print("Telegram message sent successfully")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    return sub_txt

# ------------------ 自动访问 ------------------
def add_visit_task():
    if not AUTO_ACCESS or not PROJECT_URL:
        return
    try:
        requests.post(
            'https://keep.gvrander.eu.org/add-url',
            json={"url": PROJECT_URL},
            headers={"Content-Type": "application/json"}
        )
        print("Automatic access task added")
    except Exception as e:
        print(f"Failed to add URL: {e}")

# ------------------ 启动 ------------------
if __name__ == "__main__":
    generate_links()
    add_visit_task()
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
