import os
import re
import cloudscraper # Ye Cloudflare security ko bypass karega
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- BYPASS LOGIC ---
def extract_hubdrive_link(url):
    print(f"🕵️ Trying to unlock: {url}")
    try:
        # CloudScraper Browser ban kar request bhejega
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Request Bhejo
        response = scraper.get(url)
        
        # --- DEBUGGING (Logs me dikhega ki kya mila) ---
        # Agar status 403 ya 503 hai, mtlb abhi bhi block hai
        print(f"📡 Status Code: {response.status_code}")

        # Regex: Ye HubCloud ke kisi bhi domain (.space, .club, .me) ko pakdega
        pattern = r'href="(https?://hubcloud\.[a-z]+/drive/[^"]+)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
        else:
            # Agar direct link nahi mila, to check karte hain Cloudflare ne roka kya
            if "Just a moment" in response.text:
                print("❌ Cloudflare Challenge Detected")
                return "Security Check (Try again in 1 min)"
            else:
                print("⚠️ Page khula par Link nahi mila")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        
    return None

# --- WEBSITE UI ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>HubDrive Unlocker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        .box { background: #1e1e1e; padding: 25px; border-radius: 12px; width: 90%; max-width: 400px; border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #00e5ff; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #444; border-radius: 5px; background: #2c2c2c; color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #00e5ff; border: none; border-radius: 5px; color: #000; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #00b8cc; }
        .result { margin-top: 20px; padding: 15px; background: #252525; border-radius: 8px; border: 1px solid #00e5ff; word-break: break-all; }
        .error { color: #ff5252; margin-top: 15px; background: rgba(255, 82, 82, 0.1); padding: 10px; border-radius: 5px; }
        a { color: #00e5ff; font-weight: bold; text-decoration: none; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🚀 Link Unlocker</h2>
        <form method="POST">
            <input type="text" name="url" placeholder="Paste HubDrive URL..." required value="{{ request.form.get('url', '') }}">
            <button type="submit">Unlock Link</button>
        </form>
        
        {% if result %}
            {% if "Security Check" in result %}
                <div class="error">❌ <b>Protection Active</b><br>HubDrive ne server ko rok diya.<br>Kuch der baad try karein.</div>
            {% else %}
                <div class="result">
                    <p>✅ <b>Success!</b></p>
                    <a href="{{ result }}" target="_blank">📥 Click to Download</a>
                </div>
            {% endif %}
        {% elif error %}
            <div class="error">❌ Link Not Found<br><small>Pattern match failed</small></div>
        {% endif %}
    </div>
</body>
</html>
"""

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
