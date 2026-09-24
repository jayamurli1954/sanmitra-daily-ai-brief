"""
Google Drive Cloud Archival Sync for SanMitra AI News Wire.
Automatically syncs:
  - 1080p Broadcast Video (AI_Brief_YYYY-MM-DD.mp4)
  - Custom Thumbnail (thumbnail_YYYY-MM-DD.png)
  - Facebook & LinkedIn share copy
  - Subtitles (SRT)
"""

import argparse
from datetime import datetime
import os
import sys

try:
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("[!] Google API client not installed.")
    sys.exit(1)

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    # 1. Try Service Account key if configured
    sa_file = "gdrive_service_account.json"
    if os.path.exists(sa_file):
        creds = service_account.Credentials.from_service_account_file(sa_file, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)

    # 2. Try User OAuth Token (same token or gdrive_token.json)
    token_file = "gdrive_token.json" if os.path.exists("gdrive_token.json") else "token.json"
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        return build('drive', 'v3', credentials=creds)

    return None

def upload_file_to_drive(service, file_path, folder_id=None):
    if not os.path.exists(file_path):
        return None

    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    print(f"[+] Uploaded to Google Drive: {file_name} -> {file.get('webViewLink')}")
    return file

def main():
    parser = argparse.ArgumentParser(description="Sync AI Brief to Google Drive")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--folder-id", type=str, help="Google Drive destination folder ID")
    args = parser.parse_args()

    service = get_drive_service()
    if not service:
        print("[!] No Google Drive credentials found (gdrive_service_account.json or gdrive_token.json). Skipping sync.")
        return

    date_str = args.date
    files = [
        f"out/aibrief/AI_Brief_{date_str}.mp4",
        f"out/aibrief/thumbnail_{date_str}.png",
        f"out/aibrief/facebook_post.txt",
        f"out/aibrief/linkedin_post.txt",
        f"out/aibrief/captions_{date_str}.srt"
    ]

    for fp in files:
        if os.path.exists(fp):
            upload_file_to_drive(service, fp, args.folder_id)

if __name__ == "__main__":
    main()
