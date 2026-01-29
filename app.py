import os
import re
import cloudscraper
from flask import Flask, request, render_template_string
from urllib.parse import urlparse

app = Flask(__name__)

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_hubdrive_link(url):
    print(f"🕵️ Trying to unlock: {url}")
    
    # Validate URL first
    if not is_valid_url(url):
        print("❌ Invalid URL format")
        return "Invalid URL format"
    
    try:
        # Create scraper with proper settings
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=5
        )
        
        # Set headers to mimic real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        print("📡 Sending request...")
        response = scraper.get(url, headers=headers, timeout=30)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code != 200:
            return f"Server returned status {response.status_code}"
        
        # Check for Cloudflare challenge
        if "Just a moment" in response.text or "cloudflare" in response.text.lower():
            print("❌ Cloudflare challenge detected")
            return "Cloudflare Protection Active - Please try again in 1 minute"
        
        # Multiple patterns to try for different HubDrive versions
        patterns = [
            r'href=["\'](https?://(?:hubcloud|hubdrive)\.[^"\']+/drive/[^"\']+)["\']',
            r'src=["\'](https?://(?:hubcloud|hubdrive)\.[^"\']+/drive/[^"\']+)["\']',
            r'download-link["\'][^>]*?href=["\']([^"\']+)["\']',
            r'direct-download["\'][^>]*?href=["\']([^"\']+)["\']',
            r'"(https?://[^/]+/file/[^"\']+)"',
            r'"(https?://[^/]+/embed/[^"\']+)"',
            r'iframe.*?src=["\'](https?://[^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                print(f"✅ Found {len(matches)} matches with pattern")
                # Return the first valid match
                for match in matches:
                    if 'drive' in match.lower() or 'file' in match.lower():
                        print(f"🎯 Extracted link: {match}")
                        return match
        
        # If no patterns matched, try to find any hubdrive/hubcloud link
        all_links = re.findall(r'href=["\'](https?://[^"\']+)["\']', response.text)
        hub_links = [link for link in all_links if 'hubdrive' in link.lower() or 'hubcloud' in link.lower()]
        
        if hub_links:
            print(f"🔗 Found hub link: {hub_links[0]}")
            return hub_links[0]
        
        print("⚠️ No download link found in page")
        return "No download link found. The page structure might have changed."
        
    except cloudscraper.exceptions.CloudflareChallengeError:
        print("❌ Cloudflare challenge error")
        return "Cloudflare Security Challenge Failed - Try again later"
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return f"Error: {str(e)}"

# HTML Template
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>HubDrive Unlocker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 500px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(45deg, #00e5ff, #00b8cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #aaa;
            font-size: 1rem;
        }
        
        .box {
            background: rgba(30, 30, 30, 0.9);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(0, 229, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(0, 229, 255, 0.3);
            border-radius: 8px;
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #00e5ff;
            box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
        }
        
        input[type="text"]::placeholder {
            color: #888;
        }
        
        .submit-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(45deg, #00e5ff, #00b8cc);
            border: none;
            border-radius: 8px;
            color: #000;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 229, 255, 0.4);
        }
        
        .submit-btn:active {
            transform: translateY(0);
        }
        
        .result-box {
            margin-top: 25px;
            padding: 20px;
            border-radius: 10px;
            background: rgba(0, 229, 255, 0.1);
            border: 1px solid rgba(0, 229, 255, 0.3);
            animation: fadeIn 0.5s ease;
        }
        
        .success {
            color: #00ff88;
        }
        
        .error {
            color: #ff5252;
        }
        
        .download-link {
            display: block;
            margin-top: 15px;
            padding: 15px;
            background: rgba(0, 229, 255, 0.2);
            border-radius: 8px;
            color: #00e5ff;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            word-break: break-all;
        }
        
        .download-link:hover {
            background: rgba(0, 229, 255, 0.3);
            transform: translateY(-2px);
        }
        
        .instructions {
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            font-size: 14px;
            color: #aaa;
        }
        
        .instructions h3 {
            color: #00e5ff;
            margin-bottom: 10px;
        }
        
        .instructions ol {
            margin-left: 20px;
            line-height: 1.6;
        }
        
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .loader {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top: 4px solid #00e5ff;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 600px) {
            .box {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            input[type="text"] {
                padding: 12px;
            }
            
            .submit-btn {
                padding: 14px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HubDrive Unlocker</h1>
            <p>Unlock HubDrive links instantly | Fast & Secure</p>
        </div>
        
        <div class="box">
            <form method="POST" id="unlockForm" onsubmit="showLoading()">
                <div class="form-group">
                    <input type="text" name="url" 
                           placeholder="Paste your HubDrive/HubCloud link here..." 
                           required 
                           value="{{ request.form.get('url', '') }}">
                </div>
                
                <button type="submit" class="submit-btn">
                    <span>🔓 Unlock Link</span>
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="loader"></div>
                <p>Processing your link... Please wait</p>
            </div>
            
            {% if result %}
                <div class="result-box">
                    {% if "Error" in result or "Invalid" in result or "No download" in result or "Cloudflare" in result %}
                        <div class="error">
                            <h3>❌ Error</h3>
                            <p>{{ result }}</p>
                            <p style="margin-top: 10px; font-size: 14px; color: #aaa;">
                                Try again in 60 seconds or check if the URL is correct.
                            </p>
                        </div>
                    {% else %}
                        <div class="success">
                            <h3>✅ Success! Link Unlocked</h3>
                            <p>Your direct download link is ready:</p>
                            <a href="{{ result }}" class="download-link" target="_blank">
                                📥 Click here to Download
                            </a>
                            <p style="margin-top: 15px; font-size: 14px; color: #aaa;">
                                ⚠️ Link will expire. Download immediately.
                            </p>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
            
            <div class="instructions">
                <h3>📖 How to Use:</h3>
                <ol>
                    <li>Copy any HubDrive or HubCloud link</li>
                    <li>Paste it in the box above</li>
                    <li>Click "Unlock Link"</li>
                    <li>Wait a few seconds for processing</li>
                    <li>Click the download button when it appears</li>
                </ol>
            </div>
        </div>
        
        <div class="footer">
            <p>This tool is for educational purposes only.</p>
            <p>© 2026 HubDrive Unlocker | v1.0</p>
        </div>
    </div>
    
    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.submit-btn').disabled = true;
        }
        
        // Auto-hide loading after 30 seconds (fallback)
        setTimeout(function() {
            document.getElementById('loading').style.display = 'none';
            document.querySelector('.submit-btn').disabled = false;
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    result = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            result = extract_hubdrive_link(url)
    return render_template_string(HTML_CODE, result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    # Debug mode only in development
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)
