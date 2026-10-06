"""
Google Drive Cloud Archival Sync for SanMitra AI News Wire & OfficeMitra AI Insights.
Automatically syncs to the designated Google Drive folder (e.g. 'sanmitra-daily-ai-brief'):
  - 1080p Broadcast Video (AI_Brief_YYYY-MM-DD.mp4)
  - Custom Thumbnail (thumbnail_YYYY-MM-DD.png)
  - 16:9 LinkedIn Cover Banner (linkedin_cover_YYYY-MM-DD.png)
  - LinkedIn Long-Form Article (linkedin_article.md)
  - Ready-to-Publish LinkedIn Post (linkedin_post.txt)
  - Ready-to-Publish Facebook Post (facebook_post.txt)
  - Subtitles (SRT)
"""

import argparse
from datetime import datetime
import os
import sys
from typing import Dict, List, Optional

# Ensure Windows PowerShell/cmd does not crash on unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("[!] Google API client libraries not installed.")
    print("    Install them with: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

SCOPES = [
    'https://www.googleapis.com/auth/drive.file'
]

CLIENT_SECRETS_FILE = "client_secret.json"
GDRIVE_TOKEN_FILE = "gdrive_token.json"
DEFAULT_FOLDER_NAME = "sanmitra-daily-ai-brief"


def get_drive_service():
    """
    Returns an authenticated Google Drive service instance.
    Uses gdrive_token.json or runs a one-time browser OAuth flow.
    """
    # 1. Try Service Account key if configured
    sa_file = "gdrive_service_account.json"
    if os.path.exists(sa_file):
        try:
            creds = service_account.Credentials.from_service_account_file(sa_file, scopes=SCOPES)
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"[!] Service account error: {e}")

    # 2. Try User OAuth Token (gdrive_token.json or token.json)
    creds = None
    if os.path.exists(GDRIVE_TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(GDRIVE_TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"[!] Warning reading {GDRIVE_TOKEN_FILE}: {e}")
    elif os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        except Exception as e:
            print(f"[!] Warning reading token.json for Drive: {e}")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(GDRIVE_TOKEN_FILE, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            except Exception as e:
                print(f"[!] Token refresh failed: {e}. Re-authenticating...")
                creds = None

        if not creds:
            # Prevent hanging indefinitely in automated background runs / GitHub Actions
            if not sys.stdin or not sys.stdin.isatty():
                print("[!] Non-interactive environment detected: Google Drive token expired or revoked.")
                print("    Skipping Google Drive upload to prevent pipeline freeze. Run 'python upload_to_gdrive.py --auth' interactively to re-link.")
                return None

            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"[X] Client secrets file '{CLIENT_SECRETS_FILE}' not found!")
                return None

            print("=" * 70)
            print("🔑 ONE-TIME GOOGLE DRIVE AUTHORIZATION REQUIRED")
            print("    Opening browser to authorize Google Drive access for folder uploads...")
            print("=" * 70)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(GDRIVE_TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
            print(f"[+] Saved Google Drive token to {GDRIVE_TOKEN_FILE} for 100% automated future runs.")

    return build('drive', 'v3', credentials=creds)


def resolve_folder_id(service, folder_name: str = DEFAULT_FOLDER_NAME, explicit_id: Optional[str] = None) -> Optional[str]:
    """
    Resolves the destination folder ID by querying Google Drive by name if not explicitly provided.
    """
    if explicit_id:
        return explicit_id

    # Check environment variable
    env_id = os.environ.get("GDRIVE_FOLDER_ID")
    if env_id:
        return env_id

    # Query Google Drive for the folder by name
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    try:
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        if files:
            found_id = files[0]['id']
            print(f"[+] Found existing Google Drive folder '{folder_name}': ID = {found_id}")
            return found_id
        else:
            # Create the folder if it doesn't exist
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            new_id = folder.get('id')
            print(f"[+] Created new Google Drive folder '{folder_name}': ID = {new_id}")
            return new_id
    except Exception as e:
        print(f"[!] Warning resolving Google Drive folder: {e}")
        return None


def upload_file_to_drive(service, file_path: str, folder_id: Optional[str] = None):
    if not os.path.exists(file_path):
        return None

    import mimetypes
    mime, _ = mimetypes.guess_type(file_path)
    if not mime:
        if file_path.endswith('.md') or file_path.endswith('.txt') or file_path.endswith('.srt'):
            mime = 'text/plain'
        elif file_path.endswith('.png'):
            mime = 'image/png'
        elif file_path.endswith('.mp4'):
            mime = 'video/mp4'
        else:
            mime = 'application/octet-stream'

    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'mimeType': mime}
    if folder_id:
        file_metadata['parents'] = [folder_id]

    try:
        media = MediaFileUpload(file_path, mimetype=mime, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        print(f"  [+] Uploaded: {file_name:<35} -> {file.get('webViewLink')}")
        return file
    except Exception as e:
        print(f"  [X] Failed to upload {file_name}: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Sync AI Brief and LinkedIn deliverables to Google Drive")
    parser.add_argument("--date", type=str, default=datetime.now().strftime("%Y-%m-%d"), help="Episode date (YYYY-MM-DD)")
    parser.add_argument("--folder-name", type=str, default=DEFAULT_FOLDER_NAME, help="Google Drive destination folder name")
    parser.add_argument("--folder-id", type=str, help="Google Drive destination folder ID (optional)")
    parser.add_argument("--auth", action="store_true", help="Run interactive authorization only")
    args = parser.parse_args()

    service = get_drive_service()
    if not service:
        print("[!] No Google Drive credentials available. Aborting sync.")
        return

    if args.auth:
        print("[+] Google Drive authentication is valid and ready.")
        return

    folder_id = resolve_folder_id(service, folder_name=args.folder_name, explicit_id=args.folder_id)

    date_str = args.date
    files = [
        f"out/aibrief/AI_Brief_{date_str}.mp4",
        f"out/aibrief/thumbnail_{date_str}.png",
        f"out/aibrief/thumbnail_primary.png",
        f"out/aibrief/linkedin_cover_{date_str}.png",
        f"out/aibrief/linkedin_cover.png",
        f"out/aibrief/linkedin_article.md",
        f"out/aibrief/linkedin_post.txt",
        f"out/aibrief/facebook_post.txt",
        f"out/aibrief/captions_{date_str}.srt",
        f"prompts/{date_str}.md"
    ]

    print("=" * 75)
    print(f"☁️  SYNCING DELIVERABLES TO GOOGLE DRIVE FOLDER: '{args.folder_name}'")
    print(f"📁 Destination Folder ID: {folder_id or 'Root of My Drive'}")
    print("=" * 75)

    uploaded_count = 0
    for fp in files:
        if os.path.exists(fp):
            res = upload_file_to_drive(service, fp, folder_id)
            if res:
                uploaded_count += 1

    print("=" * 75)
    print(f"🎉 SYNC COMPLETED: {uploaded_count} files deposited into '{args.folder_name}'.")
    print("=" * 75)


if __name__ == "__main__":
    main()
