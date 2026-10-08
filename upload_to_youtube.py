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

# Countries where the brief may be viewed. YouTube Studio stores one map pin;
# a list of markets is set as the allowed distribution regions.
DISTRIBUTION_REGIONS = [
    # United States, United Kingdom, Australia, New Zealand
    "US", "GB", "AU", "NZ",
    # Gulf
    "AE", "SA", "QA", "KW", "BH", "OM",
    # Europe
    "AL", "AD", "AT", "BA", "BE", "BG", "BY", "CH", "CY", "CZ", "DE", "DK",
    "EE", "ES", "FI", "FR", "GR", "HR", "HU", "IE", "IS", "IT", "LI", "LT",
    "LU", "LV", "MC", "MD", "ME", "MK", "MT", "NL", "NO", "PL", "PT", "RO",
    "RS", "SE", "SI", "SK", "SM", "UA", "VA",
    # Asia
    "AF", "AM", "AZ", "BD", "BN", "BT", "CN", "GE", "HK", "ID", "IN", "JP",
    "KG", "KH", "KR", "KZ", "LA", "LK", "MM", "MN", "MO", "MY", "NP", "PH",
    "PK", "SG", "TH", "TJ", "TL", "TM", "TW", "UZ", "VN",
]


def set_distribution_regions(youtube, video_id):
    print("[*] Setting viewing regions: Asia, USA, UK, Europe, Gulf, Australia, New Zealand...")
    try:
        youtube.videos().update(
            part="contentDetails",
            body={
                "id": video_id,
                "contentDetails": {
                    "regionRestriction": {"allowed": DISTRIBUTION_REGIONS}
                },
            },
        ).execute()
        print(f"[+] Viewing regions set ({len(DISTRIBUTION_REGIONS)} countries).")
    except Exception as e:
        print(f"[!] Failed to set viewing regions: {e}")


def upload_video(youtube, file_path, title, description, tags, category_id="28", privacy_status="private", publish_at=None):
    status = {
        "privacyStatus": "private" if publish_at else privacy_status,
        "selfDeclaredMadeForKids": False,
    }
    # YouTube publishes a private video automatically at publishAt.
    if publish_at:
        status["publishAt"] = publish_at
    # Sanitize and enforce YouTube API constraints (max 5000 chars, no angle brackets)
    clean_desc = description.replace("<", "").replace(">", "")
    if len(clean_desc) > 4900:
        clean_desc = clean_desc[:4900].rsplit("\n", 1)[0] + "\n\n... (Visit sanmitra.ai for full brief)"

    safe_tags = []
    curr_len = 0
    for t in tags:
        clean_t = t.replace("<", "").replace(">", "").strip()
        if clean_t and curr_len + len(clean_t) < 400:
            safe_tags.append(clean_t)
            curr_len += len(clean_t) + 1

    body = {
        "snippet": {
            "title": title[:100], # YouTube max 100 chars
            "description": clean_desc,
            "tags": safe_tags,
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": status,
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=10 * 1024 * 1024, resumable=True)
    )

    label = f"SCHEDULED {publish_at}" if publish_at else privacy_status.upper()
    print(f"[*] Uploading video: {file_path} ({label})...")
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

def post_discussion_comment(youtube, video_id, date_str):
    date_path = f"src/aibrief/data/{date_str}.json"
    active_path = "src/aibrief/data/active_episode.json"
    target_path = date_path if os.path.exists(date_path) else active_path

    s1_title = "today's top story"
    s2_title = "enterprise AI policy"
    if os.path.exists(target_path):
        try:
            import json
            with open(target_path, "r", encoding="utf-8") as f:
                ep = json.load(f)
            stories = ep.get("stories", [])
            if len(stories) > 0:
                s1_title = stories[0].get("headline", s1_title)
            if len(stories) > 1:
                s2_title = stories[1].get("headline", s2_title)
        except Exception:
            pass

    comment_text = (
        f"💬 TODAY'S DISCUSSION: With developments surrounding '{s1_title}' and '{s2_title}', "
        f"which AI move do you believe will have the greatest impact on enterprise security and global policy?\n\n"
        f"Share your perspective in the comments below! 👇\n\n"
        f"🔔 Subscribe to SanMitra AI News Wire for daily institutional AI intelligence: "
        f"https://www.youtube.com/@SanMitraTechSolutions?sub_confirmation=1"
    )

    try:
        print(f"[*] Posting initial engagement discussion comment...")
        res = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment_text
                        }
                    }
                }
            }
        ).execute()
        print(f"[+] Discussion comment posted successfully! (ID: {res.get('id')})")
    except Exception as e:
        print(f"[!] Note: Could not post discussion comment: {e}")

def main():
    today_str = datetime.now().strftime("%Y-%m-%d")
    parser = argparse.ArgumentParser(description="Upload AI Brief to YouTube")
    parser.add_argument("--date", type=str, default=today_str, help=f"Episode date (YYYY-MM-DD, default: {today_str})")
    parser.add_argument("--privacy", type=str, default="private", choices=["private", "unlisted", "public"], help="Video privacy status (default: private)")
    parser.add_argument("--video-file", type=str, help="Custom video file path")
    parser.add_argument("--thumb-file", type=str, help="Custom thumbnail file path")
    parser.add_argument("--meta-file", type=str, help="Custom metadata file path")
    parser.add_argument("--video-id", type=str, help="Existing YouTube video ID to set thumbnail for")
    parser.add_argument("--publish-at", type=str, help="UTC time to publish, RFC3339, for example 2026-10-03T02:00:00Z")
    args = parser.parse_args()

    date_str = args.date
    # Hard gate: do not publish a video whose sources are not in the approved prompt.
    from validate_episode_sources import validate
    if not validate(date_str):
        print("[X] Source traceability gate failed. Not uploading.")
        sys.exit(1)

    if args.thumb_file:
        thumb_path = args.thumb_file if os.path.exists(args.thumb_file) else ""
    else:
        thumb_path = f"out/aibrief/thumbnail_{date_str}.png"
        if not os.path.exists(thumb_path) and os.path.exists("out/aibrief/thumbnail_A.png"):
            thumb_path = "out/aibrief/thumbnail_A.png"

    youtube = get_authenticated_service()

    if args.video_id:
        video_id = args.video_id
        print(f"[*] Using existing Video ID: {video_id}")
    else:
        video_path = args.video_file or f"out/aibrief/AI_Brief_{date_str}.mp4"
        meta_path = args.meta_file or f"out/aibrief/youtube_metadata_{date_str}.txt"
        if not os.path.exists(meta_path):
            meta_path = "out/aibrief/youtube_metadata.txt"

        if not os.path.exists(video_path):
            print(f"[X] Video file not found: {video_path}")
            print("    Please render the video first or specify --video-file.")
            sys.exit(1)

        title, description, tags = parse_metadata_file(meta_path)
        video_id = upload_video(
            youtube,
            video_path,
            title,
            description,
            tags,
            privacy_status=args.privacy,
            publish_at=args.publish_at,
        )
    
    if os.path.exists(thumb_path):
        set_thumbnail(youtube, video_id, thumb_path)

    set_distribution_regions(youtube, video_id)

    # YouTube does not allow comments on private videos. Unlisted and public do.
    if args.publish_at or args.privacy == "private":
        print("[*] Discussion comment skipped. YouTube does not allow comments while a video is private.")
        print("    Set the video to Unlisted or Public, then run this again with --privacy unlisted or --privacy public.")
    else:
        post_discussion_comment(youtube, video_id, date_str)

    print("\n" + "=" * 70)
    print("🚀 AUTOMATED YOUTUBE PUBLISHING COMPLETED!")
    print(f"📺 Video Link: https://youtu.be/{video_id}")
    if args.publish_at:
        print(f"🎯 Status:     PRIVATE until {args.publish_at}, then PUBLIC")
    else:
        print(f"🎯 Status:     {args.privacy.upper()}")
    print("=" * 70)

if __name__ == "__main__":
    main()
