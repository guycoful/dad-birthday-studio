#!/usr/bin/env python3
"""
Google Photos Shared Album Importer for Dad's 60th Birthday Studio
Usage:
    python scripts/import_google_photos.py "https://photos.app.goo.gl/..." [--act act_5] [--download]
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
import re
import json
from datetime import datetime

# Reconfigure stdout for utf-8 output on all platforms
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CHAPTER_NAMES = {
    'act_1': 'פרק 1: שנות הילדות',
    'act_2': 'פרק 2: נעורים, צבא ושנות ה-20',
    'act_3': 'פרק 3: הקמת המשפחה',
    'act_4': 'פרק 4: חוויות, טיולים ורגעים יפים',
    'act_5': 'פרק 5: חוגגים 60 לאבא'
}

def resolve_and_fetch_album_html(url):
    print(f"🔗 מתחבר לקישור האלבום: {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            final_url = resp.geturl()
            print(f"✓ כתובת אלבום סופית: {final_url[:75]}...")
            html = resp.read().decode('utf-8', errors='ignore')
            return html
    except Exception as e:
        print(f"❌ שגיאה בהתחברות לאלבום: {e}")
        return None

def extract_album_items(html):
    print("🔍 סורק ומחלץ פריטי מדיה מתוך נתוני האלבום...")
    callback_regex = re.compile(r'AF_initDataCallback\(([\s\S]*?)\);\s*<\/script>')
    items = []
    found_urls = set()

    for match in callback_regex.finditer(html):
        s = match.group(1)
        if 'data:' in s and 'sideChannel:' in s:
            dm = re.search(r'data:([\s\S]*?),\s*sideChannel:', s)
            if dm:
                try:
                    parsed = json.loads(dm.group(1).strip())
                    if isinstance(parsed, list) and len(parsed) > 1 and isinstance(parsed[1], list):
                        for it in parsed[1]:
                            if isinstance(it, list) and len(it) > 1 and it[1] and it[1][0]:
                                item_id = it[0]
                                base_url = it[1][0]
                                if base_url in found_urls:
                                    continue
                                found_urls.add(base_url)

                                w = it[1][1] if len(it[1]) > 1 else 1920
                                h = it[1][2] if len(it[1]) > 2 else 1080

                                is_video = False
                                if len(it) > 15 and it[15] is not None:
                                    is_video = True
                                elif len(it) > 12 and isinstance(it[12], dict):
                                    is_video = True
                                else:
                                    for v in it:
                                        if isinstance(v, dict) and 'video' in json.dumps(v).lower():
                                            is_video = True
                                            break

                                items.append({
                                    'id': item_id,
                                    'base_url': base_url,
                                    'width': w,
                                    'height': h,
                                    'is_video': is_video
                                })
                except Exception as e:
                    pass

    # Fallback to direct url regex
    if not items:
        url_regex = re.compile(r'https:\/\/lh3\.googleusercontent\.com\/[a-zA-Z0-9_\-]+')
        for match in url_regex.finditer(html):
            u = match.group(0)
            if len(u) > 50 and u not in found_urls:
                found_urls.add(u)
                items.append({
                    'id': f"gp_{len(items)+1}",
                    'base_url': u,
                    'width': 1920,
                    'height': 1080,
                    'is_video': False
                })

    return items

def download_media_item(base_url, target_path, is_video=False):
    url = f"{base_url}=dv" if is_video else f"{base_url}=d"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(target_path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"  ⚠️ שגיאה בהורדת {os.path.basename(target_path)}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Google Photos Album Importer")
    parser.add_argument("url", help="Google Photos shared album URL")
    parser.add_argument("--act", default="act_5", choices=['act_1', 'act_2', 'act_3', 'act_4', 'act_5'], help="Target Chapter/Act")
    parser.add_argument("--download", action="store_true", help="Download physical files to disk instead of using direct Google CDN URLs")
    parser.add_argument("--max", type=int, default=0, help="Max items to import (0 = all)")
    args = parser.parse_args()

    html = resolve_and_fetch_album_html(args.url)
    if not html:
        sys.exit(1)

    items = extract_album_items(html)
    if not items:
        print("❌ לא נמצאו פריטי מדיה באלבום. ודא שהאלבום פתוח לצפייה ציבורית.")
        sys.exit(1)

    if args.max > 0:
        items = items[:args.max]

    vids = [i for i in items if i['is_video']]
    photos = [i for i in items if not i['is_video']]
    print(f"✅ זוהו בהצלחה {len(items)} פריטים ({len(photos)} תמונות, {len(vids)} סרטונים)!")

    # Load storyboard.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)
    storyboard_path = os.path.join(repo_root, 'public', 'storyboard.json')

    if not os.path.exists(storyboard_path):
        print(f"❌ לא נמצא קובץ {storyboard_path}")
        sys.exit(1)

    with open(storyboard_path, 'r', encoding='utf-8') as f:
        sb = json.load(f)

    existing_slides = sb.get('slides', [])
    start_index = len(existing_slides) + 1
    act_title = CHAPTER_NAMES.get(args.act, 'חוגגים 60 לאבא')

    photos_dir = os.path.join(repo_root, 'public', 'photos')
    videos_dir = os.path.join(repo_root, 'public', 'videos')
    thumbs_dir = os.path.join(repo_root, 'public', 'thumbnails')

    os.makedirs(photos_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    os.makedirs(thumbs_dir, exist_ok=True)

    new_slides = []
    print(f"\n🚀 מעבד ומוסיף {len(items)} פריטים לפרק '{act_title}'...")

    for i, it in enumerate(items):
        is_vid = it['is_video']
        slide_idx = start_index + i
        item_id = it['id']

        if args.download:
            ext = 'mp4' if is_vid else 'jpg'
            fname = f"gphoto_{item_id}.{ext}"
            target_path = os.path.join(videos_dir if is_vid else photos_dir, fname)
            print(f"[{i+1}/{len(items)}] מוריד {fname}...")
            download_media_item(it['base_url'], target_path, is_vid)
            media_path = f"videos/{fname}" if is_vid else f"photos/{fname}"
        else:
            media_path = f"{it['base_url']}=dv" if is_vid else f"{it['base_url']}=w1920-h1080"
            fname = f"gphoto_{item_id}.{'mp4' if is_vid else 'jpg'}"

        new_slide = {
            "slide_id": int(datetime.now().timestamp() * 1000) + i,
            "type": "video" if is_vid else "cinematic",
            "act": args.act,
            "act_title": act_title,
            "duration": 10 if is_vid else 8,
            "caption": f"רגע מ{act_title}",
            "quote": "",
            "primary_item": {
                "index": slide_idx,
                "filename": fname,
                "cloud_path": media_path,
                "is_video": is_vid
            },
            "items": [{
                "filename": fname,
                "cloud_path": media_path,
                "is_video": is_vid
            }],
            "rotation": 0,
            "scale": 1.0,
            "offsetX": 0,
            "offsetY": 0,
            "trim": 0,
            "cropBox": None,
            "fitMode": "contain",
            "showCaption": True,
            "soundtrack_action": "continue",
            "transition_effect": "crossfade"
        }
        new_slides.append(new_slide)

    sb['slides'].extend(new_slides)
    sb['last_modified'] = datetime.now().isoformat()

    with open(storyboard_path, 'w', encoding='utf-8') as f:
        json.dump(sb, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 הושלם בהצלחה! סך הכל {len(new_slides)} שקפים חדשים נוספו ל-storyboard.json.")
    print(f"📊 סך השקפים במצגת כעת: {len(sb['slides'])}")

if __name__ == '__main__':
    main()
