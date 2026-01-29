import os
import re
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- MAIN LOGIC ---
def extract_hubdrive_link(url):
    print(f"🔄 Processing URL: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 1. Request bhejo
        response = requests.get(url, headers=headers, timeout=15)
        print(f"📡 Status Code: {response.status_code}") # Logs mein dikhega agar block hua to

        if response.status_code == 403:
            print("❌ Render IP Blocked by HubDrive")
            return "Server Blocked (Use Local PC)"

        # 2. Link Dhoondho (Flexible Regex)
        # Ye .space, .club, .me, .foo sab kuch pakdega
        pattern = r'href="(https?://hubcloud\.[a-z]+/drive/[^"]+)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        else:
            print("⚠️ Regex match nahi hua. Page content check karein.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        pass
        
    return None

# --- WEBSITE UI ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>HubDrive Extractor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #121212; color: #eee; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background: #1e1e1e; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); width: 90%; max-width: 400px; text-align: center; border: 1px solid #333; }
        h2 { color: #00e5ff; margin-bottom: 1.5rem; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; border-radius: 6px; background: #2c2c2c; color: white; box-sizing: border-box; font-size: 16px; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: #00e5ff; color: #121212; font-weight: bold; cursor: pointer; font-size: 16px; transition: 0.2s; }
        button:hover { background: #00b8cc; }
        .result-box { margin-top: 20px; padding: 15px; background: #252525; border-radius: 8px; border: 1px solid #00e5ff; word-break: break-all; }
        a { color: #00e5ff; font-weight: bold; text-decoration: none; }
        .error { color: #ff5252; margin-top: 15px; background: rgba(255, 82, 82, 0.1); padding: 10px; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚀 Link Extractor</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Paste HubDrive URL..." required value="{{ request.form.get('url', '') }}">
            <button type="submit">Extract Link</button>
        </form>
        
        {% if result %}
            {% if "Server Blocked" in result %}
                <div class="error">❌ <b>Server Blocked!</b><br>Render ki IP HubDrive ne block kar di hai.<br>Ye code PC par chalega.</div>
            {% else %}
                <div class="result-box">
                    <p>✅ <b>Link Found:</b></p>
                    <a href="{{ result }}" target="_blank">Download Here</a>
                </div>
            {% endif %}
        {% elif error %}
            <div class="error">❌ Link Not Found<br><small>Pattern match failed</small></div>
        {% endif %}
    </div>
</body>
</html>
"""

# EK HI ROUTE MEIN GET AUR POST DONO HANDLE KIYA
@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    error = False
    
    if request.method == 'POST':
        url = request.form.get('url')
        result = extract_hubdrive_link(url)
        if not result:
            error = True
            
    return render_template_string(HTML_CODE, result=result, error=error)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
