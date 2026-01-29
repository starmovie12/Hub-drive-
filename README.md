# HubDrive Unlocker

A Flask web application to unlock HubDrive/HubCloud download links by bypassing Cloudflare protection.

## Features
- 🔓 Unlock HubDrive download links
- 🛡️ Bypass Cloudflare protection
- 📱 Responsive design
- ⚡ Fast processing
- 🔒 Secure and private

## Deployment on Render

1. **Fork this repository** to your GitHub account
2. **Go to [Render](https://render.com)**
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure settings:
   - **Name:** hubdrive-unlocker (or any name)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. Click **"Create Web Service"**

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Hub-drive-.git
cd Hub-drive-
