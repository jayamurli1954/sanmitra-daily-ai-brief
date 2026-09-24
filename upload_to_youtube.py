"""
Automated YouTube Video & Thumbnail Uploader using YouTube Data API v3.
Runs completely hands-free once the one-time OAuth token is authenticated.
"""

import argparse
from datetime import datetime
import http.client
import httplib2
import os
import random
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("[!] Google API client libraries not installed.")
    print("    Install them with: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")

# Scopes needed for uploading video and setting custom thumbnail
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"[!] Error: {CLIENT_SECRETS_FILE} not found!")
                print("    Please download your OAuth 2.0 client credentials from Google Cloud Console")
                print("    and place it in this directory as 'client_secret.json'.")
                sys.exit(1)
            print("[*] Launching browser for one-time Google OAuth authorization...")
            print("    Please log into your YouTube channel account in the opened browser window.")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token for future headless runs
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
            print(f"[+] Saved authentication token to {TOKEN_FILE} for 100% automated future runs.")
            
    return build("youtube", "v3", credentials=creds)

def parse_metadata_file(filepath):
    title = ""
    description = ""
    tags = []
    
    if not os.path.exists(filepath):
        return "SanMitra AI News Wire", "Daily institutional-grade AI intelligence.", ["AI", "Tech"]
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("DESCRIPTION:\n")
    if len(parts) >= 2:
        title = parts[0].replace("TITLE:\n", "").strip()
        description = parts[1].strip()
    else:
        title = "SanMitra AI News Wire"
        description = content
    
    # Extract tags
    for word in description.split():
        if word.startswith("#"):
            tags.append(word.lstrip("#"))
            
    return title, description, tags

def upload_video(youtube, file_path, title, description, tags, category_id="28", privacy_status="public"):
    body = {
        "snippet": {
            "title": title[:100], # YouTube max 100 chars
            "description": description,
            "tags": tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        }
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    print(f"[*] Uploading video: {file_path} ({privacy_status.upper()})...")
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                print(f"    Uploaded {int(status.progress() * 100)}%...")
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"A retriable error occurred: {e}"

        if error is not None:
            print(error)
            retry += 1
            if retry > 10:
                print("[X] Max retries exceeded.")
                sys.exit(1)
            sleep_seconds = random.random() * (2 ** retry)
            print(f"Sleeping {sleep_seconds:.1f} seconds and retrying...")
            time.sleep(sleep_seconds)
            error = None

    video_id = response.get("id")
    print(f"[+] Video uploaded successfully! Video ID: {video_id}")
    print(f"    🔗 Watch URL: https://youtu.be/{video_id}")
    return video_id

def set_thumbnail(youtube, video_id, thumbnail_file):
    if not os.path.exists(thumbnail_file):
        print(f"[!] Thumbnail file not found: {thumbnail_file}")
        return
    print(f"[*] Uploading custom thumbnail: {thumbnail_file}...")
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file)
        ).execute()
        print("[+] Custom thumbnail set successfully!")
    except Exception as e:
        print(f"[!] Failed to upload thumbnail: {e}")

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="Upload AI Brief to YouTube")
    parser.add_argument("--date", type=str, default=today_str, help=f"Episode date (YYYY-MM-DD, default: {today_str})")
    parser.add_argument("--privacy", type=str, default="public", choices=["public", "private", "unlisted"], help="Video privacy status")
    parser.add_argument("--video-file", type=str, help="Custom video file path")
    parser.add_argument("--thumb-file", type=str, help="Custom thumbnail file path")
    parser.add_argument("--video-id", type=str, help="Existing YouTube video ID to set thumbnail for")
    args = parser.parse_args()

    date_str = args.date
    thumb_path = args.thumb_file or f"out/aibrief/thumbnail_{date_str}.png"
    if not os.path.exists(thumb_path) and os.path.exists("out/aibrief/thumbnail_A.png"):
        thumb_path = "out/aibrief/thumbnail_A.png"

    youtube = get_authenticated_service()

    if args.video_id:
        video_id = args.video_id
        print(f"[*] Using existing Video ID: {video_id}")
    else:
        video_path = args.video_file or f"out/aibrief/AI_Brief_{date_str}.mp4"
        meta_path = "out/aibrief/youtube_metadata.txt"

        if not os.path.exists(video_path):
            print(f"[X] Video file not found: {video_path}")
            print("    Please render the video first or specify --video-file.")
            sys.exit(1)

        title, description, tags = parse_metadata_file(meta_path)
        video_id = upload_video(youtube, video_path, title, description, tags, privacy_status=args.privacy)
    
    if os.path.exists(thumb_path):
        set_thumbnail(youtube, video_id, thumb_path)

    print("\n" + "=" * 70)
    print("🚀 AUTOMATED YOUTUBE PUBLISHING COMPLETED!")
    print(f"📺 Video Link: https://youtu.be/{video_id}")
    print(f"🎯 Status:     {args.privacy.upper()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
