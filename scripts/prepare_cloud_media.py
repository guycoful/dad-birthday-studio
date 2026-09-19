import os
import json
import shutil
from PIL import Image, ImageOps

def prepare_cloud_assets():
    src_base = 'projects/dad-birthday-60'
    dst_base = 'projects/dad-birthday-studio'
    public_dir = os.path.join(dst_base, 'public')
    
    photos_dst = os.path.join(public_dir, 'photos')
    thumbs_dst = os.path.join(public_dir, 'thumbnails')
    audio_dst = os.path.join(public_dir, 'audio')
    enhanced_dst = os.path.join(public_dir, 'enhanced_photos')
    videos_dst = os.path.join(public_dir, 'videos')
    
    for d in [photos_dst, thumbs_dst, audio_dst, enhanced_dst, videos_dst]:
        os.makedirs(d, exist_ok=True)
        
    print("1. Optimizing photos for web deployment...")
    photos_src = os.path.join(src_base, 'processed_photos')
    count = 0
    total_orig_bytes = 0
    total_opt_bytes = 0
    
    for f in os.listdir(photos_src):
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            sp = os.path.join(photos_src, f)
            dp = os.path.join(photos_dst, f)
            sz_orig = os.path.getsize(sp)
            total_orig_bytes += sz_orig
            
            try:
                with Image.open(sp) as im:
                    im = ImageOps.exif_transpose(im)
                    # Resize max 1920x1080 while maintaining aspect ratio
                    im.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                    im = im.convert('RGB')
                    im.save(dp, 'JPEG', quality=85, optimize=True)
                total_opt_bytes += os.path.getsize(dp)
                count += 1
            except Exception as e:
                # fallback copy
                shutil.copyfile(sp, dp)
                total_opt_bytes += os.path.getsize(dp)
                count += 1
                
    print(f"Optimized {count} photos: {total_orig_bytes / (1024*1024):.1f} MB -> {total_opt_bytes / (1024*1024):.1f} MB")
    
    print("2. Copying thumbnails...")
    thumbs_src = os.path.join(src_base, 'thumbnails')
    if os.path.exists(thumbs_src):
        for f in os.listdir(thumbs_src):
            sp = os.path.join(thumbs_src, f)
            dp = os.path.join(thumbs_dst, f)
            shutil.copyfile(sp, dp)
            
    print("3. Copying audio...")
    audio_src = os.path.join(src_base, 'audio')
    if os.path.exists(audio_src):
        for f in os.listdir(audio_src):
            sp = os.path.join(audio_src, f)
            dp = os.path.join(audio_dst, f)
            if os.path.isfile(sp):
                shutil.copyfile(sp, dp)
            
    print("4. Copying enhanced/colorized photos...")
    enh_src = os.path.join(src_base, 'enhanced_photos')
    if os.path.exists(enh_src):
        for f in os.listdir(enh_src):
            sp = os.path.join(enh_src, f)
            dp = os.path.join(enhanced_dst, f)
            if os.path.isfile(sp):
                shutil.copyfile(sp, dp)
            
    print("5. Formatting master storyboard with clean relative cloud paths...")
    # Load user's latest saved storyboard
    saved_json_path = 'videos/info_videos/storyboard_saved.json'
    if os.path.exists(saved_json_path):
        with open(saved_json_path, 'r', encoding='utf-8') as f:
            slides = json.load(f)
    else:
        with open(os.path.join(src_base, 'chronological_timeline.json'), 'r', encoding='utf-8') as f:
            d = json.load(f)
            slides = d['slides']
            
    # Clean paths for cloud hosting
    for s in slides:
        fn = s['primary_item']['filename']
        # Check if colorized exists
        enh_name = f"colorized_{fn.split('.')[0]}.png"
        if os.path.exists(os.path.join(enhanced_dst, enh_name)):
            s['colorized_path'] = f"enhanced_photos/{enh_name}"
            
        if s.get('type') == 'video':
            s['primary_item']['cloud_path'] = f"videos/{fn}"
        else:
            s['primary_item']['cloud_path'] = f"photos/{fn}"
            
        for itm in s.get('items', []):
            if itm.get('is_video'):
                itm['cloud_path'] = f"videos/{itm['filename']}"
            else:
                itm['cloud_path'] = f"photos/{itm['filename']}"
                
    master_timeline = {
        "title": "סטודיו סרטון יום הולדת 60 לאבא צחי",
        "total_slides": len(slides),
        "slides": slides
    }
    
    out_json = os.path.join(public_dir, 'storyboard.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(master_timeline, f, indent=2, ensure_ascii=False)
        
    out_default = os.path.join(public_dir, 'default_storyboard.json')
    with open(out_default, 'w', encoding='utf-8') as f:
        json.dump(master_timeline, f, indent=2, ensure_ascii=False)
        
    print(f"Storyboard successfully created at {out_json} with {len(slides)} slides!")

if __name__ == '__main__':
    prepare_cloud_assets()
