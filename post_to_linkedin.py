"""
Posts the day's AI brief to LinkedIn once the YouTube episode is public.

    python post_to_linkedin.py --auth              # one-time sign-in (again every ~60 days)
    python post_to_linkedin.py --due               # run by run_linkedin_post.bat each morning
    python post_to_linkedin.py --due --dry-run     # show what would be posted
    python post_to_linkedin.py --date 2026-11-02   # post that day's brief now (recovery)

The nightly run (run_autonomous_brief.py) queues the post after the YouTube
upload: out/aibrief/linkedin_queue/<date>.txt is the post text (edit it before
9:30 if you want) and <date>.json holds the video link and publish time.

LinkedIn's API cannot publish or schedule long-form articles, so this posts a
feed post: header, opening paragraph, video link and the day's headlines. If
your own cover is saved as prompts/editor/<date>_cover.png (or .jpg) it is
posted as the image; otherwise the post shows the video as a link card with
the episode thumbnail.

Needs a LinkedIn developer app with the "Share on LinkedIn" and "Sign In with
LinkedIn using OpenID Connect" products, and http://localhost:8765/callback as
an authorised redirect URL. Its Client ID and Secret go in linkedin_client.json
({"client_id": "...", "client_secret": "..."}) or the LINKEDIN_CLIENT_ID and
LINKEDIN_CLIENT_SECRET environment variables.
"""

import argparse
import glob
import http.server
import json
import os
import re
import secrets
import sys
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone

import requests

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

QUEUE_DIR = os.path.join("out", "aibrief", "linkedin_queue")
EDITOR_DIR = os.path.join("prompts", "editor")
TOKEN_FILE = "linkedin_token.json"
CLIENT_FILE = "linkedin_client.json"
REDIRECT_URI = "http://localhost:8765/callback"
SCOPES = "openid profile w_member_social"
API = "https://api.linkedin.com/rest"
IST = timezone(timedelta(hours=5, minutes=30))
# A queued post this late is yesterday's news: it is dropped, not posted.
STALE_AFTER = timedelta(hours=24)
TOKEN_WARN = timedelta(days=7)


# ---------------------------------------------------------------- queue

def queue_post(ep, video_url, publish_at=None):
    """Called by run_autonomous_brief.py after a successful upload. publish_at is
    the UTC time YouTube makes the video public ("2026-11-02T04:00:00Z"); None
    means it is public already."""
    from src.aibrief.generate_linkedin_article import build_linkedin_post
    date_str = ep["date"]
    os.makedirs(QUEUE_DIR, exist_ok=True)
    with open(os.path.join(QUEUE_DIR, f"{date_str}.txt"), "w", encoding="utf-8") as f:
        f.write(build_linkedin_post(ep, video_url))
    meta = {"date": date_str, "video_url": video_url,
            "publish_at": publish_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "weekly": bool(ep.get("weekly"))}
    with open(os.path.join(QUEUE_DIR, f"{date_str}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[+] LinkedIn post queued for {meta['publish_at']}: {QUEUE_DIR}/{date_str}.txt")


def _parse_utc(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _save_meta(meta):
    with open(os.path.join(QUEUE_DIR, f"{meta['date']}.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def video_is_public(video_url):
    """YouTube's oEmbed answers 200 only for public (or unlisted) videos, so a
    scheduled video that has not gone live yet, or failed to, is not posted."""
    try:
        r = requests.get("https://www.youtube.com/oembed",
                         params={"url": video_url, "format": "json"}, timeout=20)
        return r.status_code == 200
    except requests.RequestException:
        return False


def cover_image(date_str):
    for ext in ("png", "jpg", "jpeg"):
        path = os.path.join(EDITOR_DIR, f"{date_str}_cover.{ext}")
        if os.path.exists(path):
            return path
    return None


# ---------------------------------------------------------------- text

# LinkedIn's "little text" format treats these as markup; unescaped, the post is
# rejected or cut short at the first one.
_RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")
_HASHTAG = re.compile(r"(?<![\w#])#(\w+)")


def to_little_text(text):
    """Escape the post text, keeping hashtags as real (clickable) hashtags."""
    parts, last = [], 0
    for m in _HASHTAG.finditer(text):
        parts.append(_RESERVED.sub(r"\\\1", text[last:m.start()]))
        parts.append("{hashtag|\\#|%s}" % m.group(1))
        last = m.end()
    parts.append(_RESERVED.sub(r"\\\1", text[last:]))
    return "".join(parts)


# ---------------------------------------------------------------- auth

def _client():
    cid, secret = os.environ.get("LINKEDIN_CLIENT_ID"), os.environ.get("LINKEDIN_CLIENT_SECRET")
    if not (cid and secret) and os.path.exists(CLIENT_FILE):
        with open(CLIENT_FILE, "r", encoding="utf-8") as f:
            c = json.load(f)
        cid, secret = c.get("client_id"), c.get("client_secret")
    if not (cid and secret):
        sys.exit(f"[X] LinkedIn app credentials missing: create {CLIENT_FILE} with client_id and client_secret.")
    return cid, secret


def _save_token(tok, person_urn=None):
    now = datetime.now(timezone.utc)
    data = {"access_token": tok["access_token"],
            "expires_at": (now + timedelta(seconds=int(tok.get("expires_in", 0)))).strftime("%Y-%m-%dT%H:%M:%SZ")}
    if tok.get("refresh_token"):
        data["refresh_token"] = tok["refresh_token"]
        data["refresh_expires_at"] = (now + timedelta(seconds=int(tok.get("refresh_token_expires_in", 0)))
                                      ).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not person_urn:
        r = requests.get("https://api.linkedin.com/v2/userinfo",
                         headers={"Authorization": f"Bearer {data['access_token']}"}, timeout=30)
        r.raise_for_status()
        person_urn = f"urn:li:person:{r.json()['sub']}"
    data["person_urn"] = person_urn
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return data


def authorize():
    """Opens LinkedIn's sign-in page and catches the redirect on localhost:8765."""
    cid, secret = _client()
    state = secrets.token_urlsafe(16)
    url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(
        {"response_type": "code", "client_id": cid, "redirect_uri": REDIRECT_URI, "state": state, "scope": SCOPES})
    got = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<p>LinkedIn sign-in received. You can close this tab.</p>".encode())

        def log_message(self, *args):
            pass

    print(f"[*] Opening LinkedIn sign-in. If no browser opens, visit:\n    {url}")
    webbrowser.open(url)
    server = http.server.HTTPServer(("localhost", 8765), Handler)
    while not got:
        server.handle_request()
    server.server_close()
    if got.get("state") != state or "code" not in got:
        sys.exit(f"[X] LinkedIn sign-in failed: {got.get('error_description') or got}")
    r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
        "grant_type": "authorization_code", "code": got["code"], "redirect_uri": REDIRECT_URI,
        "client_id": cid, "client_secret": secret}, timeout=30)
    r.raise_for_status()
    data = _save_token(r.json())
    print(f"[+] Signed in to LinkedIn. Token saved to {TOKEN_FILE}, valid until {data['expires_at']}.")


def load_token(now=None):
    """The saved token, refreshed when LinkedIn gave a refresh token. None when
    there is no usable token (run --auth)."""
    now = now or datetime.now(timezone.utc)
    if not os.path.exists(TOKEN_FILE):
        print(f"[X] No LinkedIn token. Run: python post_to_linkedin.py --auth")
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        tok = json.load(f)
    expires = _parse_utc(tok["expires_at"])
    if expires - now < TOKEN_WARN and tok.get("refresh_token") and _parse_utc(tok["refresh_expires_at"]) > now:
        cid, secret = _client()
        r = requests.post("https://www.linkedin.com/oauth/v2/accessToken", data={
            "grant_type": "refresh_token", "refresh_token": tok["refresh_token"],
            "client_id": cid, "client_secret": secret}, timeout=30)
        if r.ok:
            tok = _save_token(r.json(), tok["person_urn"])
            expires = _parse_utc(tok["expires_at"])
    if expires <= now:
        print(f"[X] LinkedIn token expired on {tok['expires_at']}. Run: python post_to_linkedin.py --auth")
        return None
    if expires - now < TOKEN_WARN:
        print(f"[!] LinkedIn token expires on {tok['expires_at']}. Run: python post_to_linkedin.py --auth")
    return tok


# ---------------------------------------------------------------- API

def api_versions(now=None):
    """LinkedIn's REST API wants a monthly version (YYYYMM) and retires each
    after about a year. Last month's is tried first, then the three before."""
    now = now or datetime.now(timezone.utc)
    y, m = now.year, now.month
    for _ in range(4):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        yield f"{y}{m:02d}"


def _call(method, path, token, **kwargs):
    for version in api_versions():
        r = requests.request(method, f"{API}/{path}", timeout=60, headers={
            "Authorization": f"Bearer {token['access_token']}", "LinkedIn-Version": version,
            "X-Restli-Protocol-Version": "2.0.0", "Content-Type": "application/json"}, **kwargs)
        # 426: that version is not (or no longer) served.
        if r.status_code != 426:
            return r
    return r


def upload_image(token, path):
    r = _call("POST", "images?action=initializeUpload", token,
              json={"initializeUploadRequest": {"owner": token["person_urn"]}})
    r.raise_for_status()
    value = r.json()["value"]
    with open(path, "rb") as f:
        up = requests.put(value["uploadUrl"], data=f.read(), timeout=120,
                          headers={"Authorization": f"Bearer {token['access_token']}"})
    up.raise_for_status()
    return value["image"]


def build_payload(token, meta, text, image_urn=None, as_cover=False):
    payload = {
        "author": token["person_urn"],
        "commentary": to_little_text(text),
        "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if as_cover:
        payload["content"] = {"media": {"id": image_urn, "altText": f"SanMitra AI News Wire, {meta['date']}"}}
    else:
        dt = datetime.strptime(meta["date"], "%Y-%m-%d")
        article = {"source": meta["video_url"],
                   "title": (f"Weekly AI Round-up — {dt.strftime('%d %B %Y')}" if meta.get("weekly")
                             else f"SanMitra AI News Wire — AI Brief, {dt.strftime('%d %B %Y')}")}
        if image_urn:
            article["thumbnail"] = image_urn
        payload["content"] = {"article": article}
    return payload


def publish(token, meta, text, dry_run=False):
    """Posts and returns the post's URL (None on a dry run)."""
    cover = cover_image(meta["date"])
    thumb = os.path.join("out", "aibrief", f"thumbnail_{meta['date']}.png")
    image_path = cover or (thumb if os.path.exists(thumb) else None)
    if dry_run:
        print(f"[dry run] {'cover image ' + cover if cover else 'link card, thumbnail ' + str(image_path)}")
        print(json.dumps(build_payload(token, meta, text, "urn:li:image:DRYRUN" if image_path else None,
                                       bool(cover)), indent=2, ensure_ascii=False))
        return None
    image_urn = upload_image(token, image_path) if image_path else None
    r = _call("POST", "posts", token, json=build_payload(token, meta, text, image_urn, bool(cover)))
    if r.status_code != 201:
        raise RuntimeError(f"LinkedIn rejected the post ({r.status_code}): {r.text[:500]}")
    return f"https://www.linkedin.com/feed/update/{r.headers.get('x-restli-id')}/"


# ---------------------------------------------------------------- run

def post_queued(dates=None, now=None, dry_run=False, force=False):
    """Posts each queued brief that is due and not yet posted. dates limits it to
    those days; force skips the time and staleness checks (not the video check).
    Returns False if a post failed."""
    now = now or datetime.now(timezone.utc)
    ok, token = True, None
    for path in sorted(glob.glob(os.path.join(QUEUE_DIR, "*.json"))):
        with open(path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if dates and meta["date"] not in dates:
            continue
        if meta.get("posted_url") or (meta.get("skipped") and not force):
            continue
        due = _parse_utc(meta["publish_at"])
        if not force and now < due:
            print(f"[ ] {meta['date']}: not due until {meta['publish_at']}")
            continue
        if not force and now - due > STALE_AFTER:
            print(f"[!] {meta['date']}: queued for {meta['publish_at']}, now too late to post. Skipped.")
            if not dry_run:
                meta["skipped"] = "stale"
                _save_meta(meta)
            continue
        if not video_is_public(meta["video_url"]):
            print(f"[ ] {meta['date']}: {meta['video_url']} is not public yet; will try again.")
            continue
        token = token or load_token(now)
        if not token and dry_run:
            token = {"person_urn": "urn:li:person:DRYRUN"}
        if not token:
            return False
        with open(os.path.join(QUEUE_DIR, f"{meta['date']}.txt"), "r", encoding="utf-8") as f:
            text = f.read().strip()
        try:
            url = publish(token, meta, text, dry_run)
        except Exception as e:
            print(f"[X] {meta['date']}: LinkedIn post failed: {e}")
            ok = False
            continue
        if url:
            meta["posted_url"] = url
            meta["posted_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            _save_meta(meta)
            print(f"[+] {meta['date']}: posted to LinkedIn: {url}")
    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post the daily AI brief to LinkedIn")
    parser.add_argument("--auth", action="store_true", help="Sign in to LinkedIn and save the token")
    parser.add_argument("--due", action="store_true", help="Post every queued brief whose video is now public")
    parser.add_argument("--date", help="Post this day's queued brief now (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Print the post instead of publishing it")
    args = parser.parse_args()

    if args.auth:
        authorize()
    elif args.date:
        sys.exit(0 if post_queued([args.date], dry_run=args.dry_run, force=True) else 1)
    elif args.due:
        sys.exit(0 if post_queued(dry_run=args.dry_run) else 1)
    else:
        parser.print_help()
