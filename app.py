import os
import re
import requests
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ✅ VARIABLE - Yaha URL change karo
HUBDRIVE_URL = "https://hubdrive.space/file/4189964814"

def extract_hubdrive_link(url):
    """Kisi bhi HubDrive URL se link extract karo"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        # Multiple patterns try karo
        patterns = [
            r'href="(https?://hubcloud\.[^/]+/drive/[^"]+)"',
            r'src="(https?://hubcloud\.[^/]+/drive/[^"]+)"',
            r'"(https?://[^"]*hubcloud[^"]*)"',
            r'download-link["\'].*?href="([^"]+)"',
            r'direct-download["\'].*?href="([^"]+)"',
            r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
            r'<a[^>]*href="([^"]*hubcloud[^"]*)"[^>]*>',
            r'<iframe[^>]*src="([^"]+)"[^>]*>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.text)
            if match:
                extracted = match.group(1)
                # Clean the URL
                if extracted.startswith('//'):
                    extracted = 'https:' + extracted
                return extracted
                
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# HTML Template
HTML_CODE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HubDrive Link Extractor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 28px;
            margin-bottom: 10px;
            color: #fff;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }
        
        .current-url {
            background: rgba(0, 0, 0, 0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            word-break: break-all;
        }
        
        .url-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 5px;
        }
        
        .url-value {
            font-family: monospace;
            font-size: 14px;
            color: #4cd964;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin: 20px 0;
        }
        
        button {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-extract {
            background: linear-gradient(45deg, #4cd964, #5ac8fa);
            color: white;
        }
        
        .btn-extract:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 217, 100, 0.4);
        }
        
        .btn-change {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .btn-change:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            display: none;
        }
        
        .success {
            background: rgba(76, 217, 100, 0.2);
            border: 2px solid #4cd964;
            display: block;
        }
        
        .error {
            background: rgba(255, 59, 48, 0.2);
            border: 2px solid #ff3b30;
            display: block;
        }
        
        .result-title {
            font-size: 16px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .download-link {
            display: block;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            color: #5ac8fa;
            text-decoration: none;
            word-break: break-all;
            margin-top: 10px;
            border: 1px solid rgba(90, 200, 250, 0.3);
            transition: all 0.3s ease;
        }
        
        .download-link:hover {
            background: rgba(90, 200, 250, 0.2);
            transform: translateY(-1px);
        }
        
        .change-url-form {
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
        }
        
        .change-url-form.active {
            display: block;
            animation: slideDown 0.3s ease;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 14px;
            margin-bottom: 10px;
        }
        
        input[type="text"]:focus {
            outline: none;
            background: rgba(255, 255, 255, 0.15);
        }
        
        .btn-update {
            background: linear-gradient(45deg, #ff9500, #ff5e3a);
            color: white;
            width: 100%;
        }
        
        .btn-update:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 149, 0, 0.4);
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top: 4px solid #4cd964;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .example-urls {
            margin-top: 15px;
            font-size: 12px;
        }
        
        .example-urls span {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            margin: 0 5px;
            cursor: pointer;
        }
        
        .example-urls span:hover {
            background: rgba(255, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 HubDrive Link Extractor</h1>
            <p class="subtitle">Variable method se link extract kare</p>
        </div>
        
        <div class="current-url">
            <div class="url-label">Current URL in Variable:</div>
            <div class="url-value" id="currentUrl">{{ current_url }}</div>
        </div>
        
        <div class="button-group">
            <button class="btn-extract" onclick="extractLink()">
                🔍 Extract Link
            </button>
            <button class="btn-change" onclick="showChangeForm()">
                ✏️ Change URL
            </button>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing... Please wait</p>
        </div>
        
        {% if result %}
            <div class="result success">
                <div class="result-title">
                    <span>✅ Link Found!</span>
                </div>
                <a href="{{ result }}" class="download-link" target="_blank">
                    📥 {{ result[:50] }}...
                </a>
                <p style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
                    Click to open download link
                </p>
            </div>
        {% elif error %}
            <div class="result error">
                <div class="result-title">
                    <span>❌ Link Not Found</span>
                </div>
                <p>Pattern match failed. Try different URL.</p>
            </div>
        {% endif %}
        
        <div class="change-url-form" id="changeForm">
            <h3 style="margin-bottom: 15px;">Change Variable URL</h3>
            <input type="text" id="newUrl" 
                   placeholder="Enter new HubDrive URL..." 
                   value="{{ current_url }}">
            <button class="btn-update" onclick="updateUrl()">
                🔄 Update Variable
            </button>
            <div class="example-urls" style="margin-top: 10px;">
                <small>Try: </small>
                <span onclick="setExample('https://hubdrive.space/file/4189964814')">Example 1</span>
                <span onclick="setExample('https://hubdrive.space/file/2695470827')">Example 2</span>
                <span onclick="setExample('https://hubdrive.club/file/12345')">Example 3</span>
            </div>
        </div>
        
        <div class="footer">
            <p>Made with Flask | Variable Method | Simple & Effective</p>
            <p>🔧 Server reload required after URL change</p>
        </div>
    </div>
    
    <script>
        let currentUrl = "{{ current_url }}";
        
        function extractLink() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('changeForm').classList.remove('active');
            
            // Reload page to extract with current URL
            setTimeout(() => {
                window.location.href = '/extract';
            }, 1000);
        }
        
        function showChangeForm() {
            const form = document.getElementById('changeForm');
            form.classList.toggle('active');
        }
        
        function updateUrl() {
            const newUrl = document.getElementById('newUrl').value;
            if (newUrl && newUrl.includes('http')) {
                // Send to server to update variable
                fetch('/update_url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'url=' + encodeURIComponent(newUrl)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('✅ URL updated successfully! Server will reload.');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                });
            } else {
                alert('Please enter a valid URL');
            }
        }
        
        function setExample(url) {
            document.getElementById('newUrl').value = url;
        }
        
        // Auto-hide loading after 10 seconds
        setTimeout(() => {
            document.getElementById('loading').style.display = 'none';
        }, 10000);
        
        // Show result if present
        {% if result or error %}
            setTimeout(() => {
                document.getElementById('loading').style.display = 'none';
            }, 500);
        {% endif %}
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_CODE, 
                                 current_url=HUBDRIVE_URL,
                                 result=None,
                                 error=None)

@app.route('/extract')
def extract():
    """Extract link from current URL"""
    link = extract_hubdrive_link(HUBDRIVE_URL)
    if link:
        return render_template_string(HTML_CODE,
                                    current_url=HUBDRIVE_URL,
                                    result=link,
                                    error=None)
    else:
        return render_template_string(HTML_CODE,
                                    current_url=HUBDRIVE_URL,
                                    result=None,
                                    error=True)

@app.route('/update_url', methods=['POST'])
def update_url():
    """Update the global URL variable"""
    global HUBDRIVE_URL
    new_url = request.form.get('url', '').strip()
    if new_url:
        HUBDRIVE_URL = new_url
        return {'success': True, 'new_url': HUBDRIVE_URL}
    return {'success': False}

@app.route('/get_current_url')
def get_current_url():
    """Get current URL for AJAX"""
    return {'url': HUBDRIVE_URL}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Server starting...")
    print(f"🔗 Current URL in variable: {HUBDRIVE_URL}")
    print(f"🌐 Open: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
