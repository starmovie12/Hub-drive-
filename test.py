import sys
sys.path.append('.')
from app import extract_hubdrive_link

# Test with actual HubDrive link
test_url = "https://hubdrive.space/file/228100"
print(f"Testing with: {test_url}")
result = extract_hubdrive_link(test_url)
print(f"Result: {result}")
