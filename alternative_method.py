import requests
import re

def alternative_extract(url):
    """Alternative method using different approach"""
    
    # Try direct API call approach
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': url
    }
    
    # Try to find file ID from URL
    file_id_match = re.search(r'/file/(\d+)', url)
    if file_id_match:
        file_id = file_id_match.group(1)
        # Try different API endpoints
        api_urls = [
            f'https://hubdrive.space/api/file/{file_id}',
            f'https://hubdrive.space/ajax.php?cmd=download&id={file_id}',
            f'https://hubdrive.space/download/{file_id}',
        ]
        
        for api_url in api_urls:
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Try to parse JSON
                    try:
                        data = response.json()
                        if 'url' in data:
                            return data['url']
                        elif 'download' in data:
                            return data['download']
                    except:
                        # Try to find link in text
                        link_patterns = [
                            r'"url":"([^"]+)"',
                            r'"download":"([^"]+)"',
                            r'"link":"([^"]+)"',
                            r'https?://[^"\s]+/file/[^"\s]+'
                        ]
                        for pattern in link_patterns:
                            match = re.search(pattern, response.text)
                            if match:
                                return match.group(1)
            except:
                continue
    
    return None
