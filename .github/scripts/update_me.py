#!/usr/bin/env python3
"""Fetch the latest book / songs / film for the Me page and write me-data.json.

Reads credentials from environment variables (set as GitHub Actions secrets):
  LASTFM_KEY, LASTFM_USER, GOODREADS_RSS, LETTERBOXD_USER
Only the single most-recent item from each source is stored — no profile links.
"""
import os, re, json, html, datetime, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (ewot325.github.io me-page updater)"}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def strip_cdata(s):
    s = s.strip()
    m = re.match(r"<!\[CDATA\[(.*?)\]\]>", s, re.S)
    return (m.group(1) if m else s).strip()

LASTFM_KEY = os.environ["LASTFM_KEY"]
LASTFM_USER = os.environ["LASTFM_USER"]
GOODREADS_RSS = os.environ["GOODREADS_RSS"]
LETTERBOXD_USER = os.environ["LETTERBOXD_USER"]

data = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# ---- Music: Last.fm top track (rolling 7-day and 30-day windows) ----
def top_track(period):
    url = (f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks"
           f"&user={LASTFM_USER}&period={period}&limit=1"
           f"&api_key={LASTFM_KEY}&format=json")
    j = json.loads(fetch(url))
    tracks = j.get("toptracks", {}).get("track", [])
    if isinstance(tracks, dict):
        tracks = [tracks]
    if not tracks:
        return None
    t = tracks[0]
    img = ""
    for im in t.get("image", []):
        if im.get("size") in ("extralarge", "large") and im.get("#text"):
            img = im["#text"]
    if "2a96cbd8b46e442fc41c2b86b821562f" in img:  # Last.fm "no cover" placeholder
        img = ""
    return {"name": t.get("name", ""),
            "artist": t.get("artist", {}).get("name", ""),
            "image": img,
            "plays": int(t.get("playcount", 0) or 0)}

try:
    data["music"] = {"week": top_track("7day"), "month": top_track("1month")}
except Exception as e:
    data["music"] = None
    print("music error:", e)

# ---- Book: Goodreads "read" shelf RSS (most recent item) ----
try:
    xml = fetch(GOODREADS_RSS)
    m = re.search(r"<item>(.*?)</item>", xml, re.S)
    book = None
    if m:
        it = m.group(1)
        def g(tag):
            mm = re.search(r"<%s>(.*?)</%s>" % (tag, tag), it, re.S)
            return strip_cdata(html.unescape(mm.group(1))) if mm else ""
        rating = g("user_rating")
        book = {"title": g("title"),
                "author": g("author_name"),
                "cover": g("book_large_image_url") or g("book_image_url"),
                "rating": int(rating) if rating.isdigit() else 0}
    data["book"] = book
except Exception as e:
    data["book"] = None
    print("book error:", e)

# ---- Film: Letterboxd RSS (most recent watched film, no review text) ----
try:
    xml = fetch(f"https://letterboxd.com/{LETTERBOXD_USER}/rss/")
    film = None
    for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
        ft = re.search(r"<letterboxd:filmTitle>(.*?)</letterboxd:filmTitle>", it, re.S)
        if not ft:
            continue  # skip lists / non-film entries
        def g2(tag):
            mm = re.search(r"<letterboxd:%s>(.*?)</letterboxd:%s>" % (tag, tag), it, re.S)
            return html.unescape(mm.group(1).strip()) if mm else ""
        poster = ""
        desc = re.search(r"<description>(.*?)</description>", it, re.S)
        if desc:
            im = re.search(r'<img src="([^"]+)"', desc.group(1))
            poster = im.group(1) if im else ""
        rating = g2("memberRating")
        film = {"title": html.unescape(ft.group(1).strip()),
                "year": g2("filmYear"),
                "rating": float(rating) if rating else None,
                "poster": poster}
        break  # only the most recent film — review text is intentionally dropped
    data["film"] = film
except Exception as e:
    data["film"] = None
    print("film error:", e)

with open("me-data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(json.dumps(data, indent=2, ensure_ascii=False))
