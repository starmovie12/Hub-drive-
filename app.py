import os
import re
import cloudscraper
import time
import random
from flask import Flask, request, render_template_string
from urllib.parse import urlparse, urljoin

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
    
    # Add referer if missing
    if 'referer' not in url.lower():
        url = f"{url}?referer=hubdrive"
    
    try:
        # Create scraper with advanced settings
        scraper = cloudscraper.create_scraper(
            interpreter='nodejs',
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            delay=8,
            recaptcha={'provider': '2captcha'}
        )
        
        # Set realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/'
        }
        
        print("📡 Sending request...")
        response = scraper.get(url, headers=headers, timeout=45)
        print(f"✅ Status Code: {response.status_code}")
        
        # Save response for debugging (optional)
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])  # First 5000 chars
        
        if response.status_code != 200:
            return f"Server returned status {response.status_code}"
        
        # Check for Cloudflare challenge
        page_text = response.text.lower()
        if "just a moment" in page_text or "cloudflare" in page_text or "ddos protection" in page_text:
            print("❌ Cloudflare challenge detected")
            return "Cloudflare Protection Active - Please try again in 2 minutes"
        
        # Method 1: Try to find direct download button/link
        patterns = [
            # Pattern for download buttons
            r'<a[^>]*href=["\'](https?://[^"\']*hubdrive[^"\']*download[^"\']*)["\'][^>]*>',
            r'<a[^>]*href=["\'](https?://[^"\']*hubcloud[^"\']*download[^"\']*)["\'][^>]*>',
            r'<a[^>]*href=["\'](https?://[^"\']*file[^"\']*)["\'][^>]*download[^>]*>',
            r'<a[^>]*href=["\'](https?://[^"\']*/file/[^"\']*)["\'][^>]*>',
            
            # Pattern for iframe embeds
            r'<iframe[^>]*src=["\'](https?://[^"\']*)["\'][^>]*>',
            r'src=["\'](https?://[^"\']*embed[^"\']*)["\']',
            
            # Pattern for JavaScript redirects
            r'window\.location\.href\s*=\s*["\'](https?://[^"\']*)["\']',
            r'window\.open\(["\'](https?://[^"\']*)["\']',
            r'\.href\s*=\s*["\'](https?://[^"\']*)["\']',
            
            # Pattern for data attributes
            r'data-url=["\'](https?://[^"\']*)["\']',
            r'data-src=["\'](https?://[^"\']*)["\']',
            r'data-file=["\'](https?://[^"\']*)["\']',
            
            # Generic patterns
            r'https?://[^"\'\s<>]*/file/[^"\'\s<>]*',
            r'https?://[^"\'\s<>]*/d/[^"\'\s<>]*',
            r'https?://[^"\'\s<>]*/embed/[^"\'\s<>]*',
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                print(f"🔍 Found {len(matches)} matches with pattern: {pattern[:50]}...")
                all_matches.extend(matches)
        
        # Filter and clean matches
        cleaned_matches = []
        for match in all_matches:
            # Clean URL
            match = match.replace('\\/', '/').replace('\/', '/')
            # Remove trailing quotes or special characters
            match = re.sub(r'["\']$', '', match)
            match = re.sub(r'["\']\).*$', '', match)
            
            # Check if it's a valid file link
            if any(keyword in match.lower() for keyword in ['/file/', '/d/', '/download', 'hubdrive', 'hubcloud', 'embed']):
                if match not in cleaned_matches:
                    cleaned_matches.append(match)
        
        print(f"🎯 Total cleaned matches: {len(cleaned_matches)}")
        
        if cleaned_matches:
            # Prioritize direct download links
            for link in cleaned_matches:
                if '/download' in link.lower() or 'direct' in link.lower():
                    print(f"✅ Selected direct download link: {link}")
                    return link
            
            # Return first valid link
            print(f"✅ Selected link: {cleaned_matches[0]}")
            return cleaned_matches[0]
        
        # Method 2: Try to extract from JavaScript variables
        js_patterns = [
            r'var\s+url\s*=\s*["\'](https?://[^"\']+)["\']',
            r'const\s+url\s*=\s*["\'](https?://[^"\']+)["\']',
            r'let\s+url\s*=\s*["\'](https?://[^"\']+)["\']',
            r'downloadUrl\s*[=:]\s*["\'](https?://[^"\']+)["\']',
            r'fileUrl\s*[=:]\s*["\'](https?://[^"\']+)["\']',
            r'source\s*[=:]\s*["\'](https?://[^"\']+)["\']',
        ]
        
        for pattern in js_patterns:
            match = re.search(pattern, response.text, re.IGNORECASE)
            if match:
                link = match.group(1).replace('\\/', '/')
                print(f"✅ Found in JavaScript: {link}")
                return link
        
        # Method 3: Try to find form action
        form_pattern = r'<form[^>]*action=["\'](https?://[^"\']+)["\'][^>]*>'
        form_match = re.search(form_pattern, response.text, re.IGNORECASE)
        if form_match:
            link = form_match.group(1)
            print(f"✅ Found form action: {link}")
            return link
        
        # Method 4: Try to decode base64 if present
        base64_pattern = r'["\']([A-Za-z0-9+/=]{20,})["\']'
        base64_matches = re.findall(base64_pattern, response.text)
        for b64 in base64_matches:
            try:
                import base64
                decoded = base64.b64decode(b64).decode('utf-8')
                if 'http' in decoded:
                    http_match = re.search(r'https?://[^\s<>"\']+', decoded)
                    if http_match:
                        print(f"✅ Found in base64: {http_match.group()}")
                        return http_match.group()
            except:
                continue
        
        print("⚠️ No download link found using patterns")
        
        # Last resort: Return the page content for manual inspection
        return "Could not extract link automatically. The page might require JavaScript execution."
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)[:100]}"

# HTML Template (same as before, but updated)
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>HubDrive Unlocker PRO</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Same CSS as before, just updating the title */
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
            max-width: 600px;
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
            background: rgba(30, 30, 30, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(0, 229, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 16px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(0, 229, 255, 0.4);
            border-radius: 10px;
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
            font-family: monospace;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #00e5ff;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.4);
            background: rgba(255, 255, 255, 0.15);
        }
        
        input[type="text"]::placeholder {
            color: #888;
            font-family: sans-serif;
        }
        
        .submit-btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(45deg, #00e5ff, #00b8cc);
            border: none;
            border-radius: 10px;
            color: #000;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        
        .submit-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 25px rgba(0, 229, 255, 0.5);
        }
        
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .result-box {
            margin-top: 25px;
            padding: 25px;
            border-radius: 12px;
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
            margin-top: 20px;
            padding: 18px;
            background: linear-gradient(45deg, rgba(0, 229, 255, 0.3), rgba(0, 184, 204, 0.3));
            border-radius: 10px;
            color: #00e5ff;
            text-decoration: none;
            font-weight: bold;
            text-align: center;
            transition: all 0.3s ease;
            word-break: break-all;
            font-family: monospace;
            border: 1px solid rgba(0, 229, 255, 0.4);
        }
        
        .download-link:hover {
            background: linear-gradient(45deg, rgba(0, 229, 255, 0.4), rgba(0, 184, 204, 0.4));
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 229, 255, 0.3);
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
            margin: 25px 0;
        }
        
        .loader {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top: 4px solid #00e5ff;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.05);
            font-size: 14px;
            color: #aaa;
            text-align: center;
        }
        
        @media (max-width: 600px) {
            .box {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            input[type="text"] {
                padding: 14px;
            }
            
            .submit-btn {
                padding: 16px;
            }
            
            .download-link {
                padding: 15px;
                font-size: 14px;
            }
        }
        
        .examples {
            margin-top: 20px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border-left: 3px solid #00e5ff;
        }
        
        .examples h4 {
            color: #00e5ff;
            margin-bottom: 8px;
        }
        
        .example-link {
            font-family: monospace;
            color: #aaa;
            font-size: 13px;
            word-break: break-all;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin: 3px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔓 HubDrive Unlocker PRO</h1>
            <p>Advanced link extraction with multiple pattern detection</p>
        </div>
        
        <div class="box">
            <form method="POST" id="unlockForm" onsubmit="showLoading()">
                <div class="form-group">
                    <input type="text" name="url" 
                           placeholder="Paste HubDrive link (e.g., https://hubdrive.space/file/XXXXX)..." 
                           required 
                           value="{{ request.form.get('url', '') }}">
                </div>
                
                <button type="submit" class="submit-btn" id="submitBtn">
                    <span>🔍 Extract Download Link</span>
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="loader"></div>
                <p>Scanning page... This may take 10-15 seconds</p>
                <div class="status">Bypassing protection...</div>
            </div>
            
            {% if result %}
                <div class="result-box">
                    {% if "Error" in result or "Invalid" in result or "Could not" in result or "Cloudflare" in result or "No download" in result %}
                        <div class="error">
                            <h3>⚠️ Extraction Failed</h3>
                            <p>{{ result }}</p>
                            <div class="instructions" style="margin-top: 15px; background: rgba(255,82,82,0.1);">
                                <h4>🛠️ Troubleshooting:</h4>
                                <ol>
                                    <li>Wait 2-3 minutes and try again</li>
                                    <li>Make sure the link is still valid</li>
                                    <li>Try a different HubDrive link</li>
                                    <li>The site might have updated protection</li>
                                </ol>
                            </div>
                        </div>
                    {% else %}
                        <div class="success">
                            <h3>✅ Download Link Found!</h3>
                            <p>Your direct download link is ready:</p>
                            <a href="{{ result }}" class="download-link" target="_blank" rel="noopener noreferrer">
                                📥 CLICK TO DOWNLOAD
                            </a>
                            <div style="margin-top: 15px; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 5px;">
                                <p style="font-size: 12px; color: #aaa; margin-bottom: 5px;">Link Preview:</p>
                                <code style="font-size: 11px; color: #888; word-break: break-all;">{{ result[:100] }}...</code>
                            </div>
                            <p style="margin-top: 15px; font-size: 14px; color: #aaa;">
                                ⚡ <strong>Important:</strong> Links may expire. Download immediately!
                            </p>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
            
            <div class="examples">
                <h4>📋 Example URLs (for testing):</h4>
                <div class="example-link">https://hubdrive.space/file/228100</div>
                <div class="example-link">https://hubdrive.club/file/XXXXX</div>
                <div class="example-link">https://hubdrive.me/file/XXXXX</div>
            </div>
            
            <div class="instructions">
                <h3>⚡ How This Works:</h3>
                <ol>
                    <li><strong>Bypass Protection:</strong> Uses advanced techniques to bypass Cloudflare</li>
                    <li><strong>Pattern Scan:</strong> Scans for 15+ different link patterns</li>
                    <li><strong>JavaScript Analysis:</strong> Extracts links from JS code</li>
                    <li><strong>Base64 Decoding:</strong> Decodes obfuscated links</li>
                    <li><strong>Direct Access:</strong> Provides you with the direct download link</li>
                </ol>
                <p style="margin-top: 10px; color: #888; font-size: 13px;">
                    <strong>Note:</strong> Some links might still fail if the site has very new protection.
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p>For educational purposes only | Use responsibly</p>
            <p>© 2026 HubDrive Unlocker PRO | Version 2.1</p>
        </div>
    </div>
    
    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('submitBtn').disabled = true;
            document.getElementById('submitBtn').innerHTML = '<span>⏳ Processing...</span>';
            
            // Update status messages
            const statusDiv = document.querySelector('.status');
            const messages = [
                'Initializing...',
                'Bypassing security...',
                'Loading page content...',
                'Scanning for links...',
                'Extracting download URL...',
                'Almost done...'
            ];
            
            let i = 0;
            const interval = setInterval(() => {
                if (i < messages.length) {
                    statusDiv.textContent = messages[i];
                    i++;
                }
            }, 2000);
            
            // Clear interval after 30 seconds (fallback)
            setTimeout(() => {
                clearInterval(interval);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('submitBtn').disabled = false;
                document.getElementById('submitBtn').innerHTML = '<span>🔍 Extract Download Link</span>';
            }, 30000);
        }
        
        // Auto-focus on input
        window.onload = function() {
            const urlInput = document.querySelector('input[name="url"]');
            if (urlInput && !urlInput.value) {
                urlInput.focus();
            }
        };
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
            print(f"📝 Processing URL: {url}")
            result = extract_hubdrive_link(url)
            print(f"📤 Result: {result}")
    return render_template_string(HTML_CODE, result=result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    print(f"🚀 Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
