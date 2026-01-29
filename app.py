import os
import re
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- AAPKA PYTHON SCRIPT (No Chrome Needed) ---
def extract_hubdrive_link(url):
    """
    Simple requests method jo aapne manga tha.
    """
    print(f"🔄 Checking URL: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # Step 1: Request bhejo
        response = requests.get(url, headers=headers, timeout=10)
        
        # Step 2: Pattern match (Regex)
        # Note: Maine '.foo' ko '.[a-z]+' kar diya hai taaki .space/.club sab pakde
        pattern = r'href="(https?://hubcloud\.[a-z]+/drive/[^"]+)"'
        match = re.search(pattern, response.text)
        
        if match:
            return match.group(1)
            
    except Exception as e:
        print(f"Error: {e}")
        pass
        
    return None

# --- WEBSITE UI (Text Box & Button) ---
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>⚡ Lite Link Extractor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #222; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #333; padding: 25px; border-radius: 10px; width: 90%; max-width: 400px; text-align: center; border: 1px solid #444; }
        input { width: 90%; padding: 12px; margin-bottom: 15px; border: none; border-radius: 5px; background: #444; color: white; }
        button { width: 100%; padding: 12px; border: none; border-radius: 5px; background: #00e5ff; color: #000; font-weight: bold; cursor: pointer; }
        .result { margin-top: 20px; word-break: break-all; color: #00ff88; }
        .error { color: #ff5555; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Lite Extractor</h2>
        <form action="/get" method="post">
            <input type="text" name="url" placeholder="Paste HubDrive URL..." required>
            <button type="submit">Extract Link</button>
        </form>
        
        {% if result %}
            <div class="result">
                <p>✅ <b>Found:</b></p>
                <a href="{{ result }}" target="_blank" style="color:#00ff88; text-decoration:none;">Download Here</a>
            </div>
        {% elif error %}
            <div class="error">❌ Link Not Found</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/get', methods=['POST'])
def get_link_route():
    # Text box se URL variable mein store hoga
    user_url = request.form.get('url')
    
    # Aapka function call hoga
    link = extract_hubdrive_link(user_url)
    
    if link:
        return render_template_string(HTML_CODE, result=link)
    else:
        return render_template_string(HTML_CODE, error=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
