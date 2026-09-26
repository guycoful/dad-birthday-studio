import json
import re

def update_studio_html():
    json_path = 'projects/dad-birthday-studio/public/storyboard.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        storyboard = json.load(f)

    json_str = json.dumps(storyboard, ensure_ascii=False)

    html_path = 'projects/dad-birthday-studio/public/index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace initialTimelineData
    prefix = 'const initialTimelineData = '
    start_idx = content.find(prefix)
    if start_idx != -1:
        end_idx = content.find(';\n', start_idx)
        if end_idx != -1:
            content = content[:start_idx + len(prefix)] + json_str + content[end_idx:]
            print('Updated initialTimelineData successfully!')

    # 2. Bump LOCAL_STORAGE_KEY to v2
    content = content.replace("const LOCAL_STORAGE_KEY = 'dad_cloud_studio_state_v1';", "const LOCAL_STORAGE_KEY = 'dad_cloud_studio_state_v2';")
    print('Bumped LOCAL_STORAGE_KEY to v2!')

    # 3. Enhance slides initialization loop with auto-correction for Slide 1, 2, and 54
    new_foreach = """function applySlideDefaults(s) {
            if (s.fitMode === undefined) s.fitMode = 'contain';
            if (s.scale === undefined) s.scale = 1.0;
            if (s.offsetX === undefined) s.offsetX = 0;
            if (s.offsetY === undefined) s.offsetY = 0;
            if (s.trim === undefined) s.trim = 0;
            if (s.showCaption === undefined) s.showCaption = true;

            const fname = (s.primary_item && s.primary_item.filename) || '';
            if (!s.colorized_path) {
                if (s.slide_id === 1 || fname.includes('259_')) {
                    s.colorized_path = 'enhanced_photos/colorized_259_IMG-20260827-WA0023.png';
                } else if (s.slide_id === 2 || fname.includes('260_')) {
                    s.colorized_path = 'enhanced_photos/colorized_260_IMG-20260827-WA0024.png';
                } else if (s.slide_id === 54 || fname.includes('319_')) {
                    s.colorized_path = 'enhanced_photos/colorized_319_IMG-20260828-WA0005.png';
                }
            }
        }
        slides.forEach(applySlideDefaults);"""

    m = re.search(r'slides\.forEach\(s =>\s*\{[\s\S]*?showCaption\s*=\s*true;\s*\}\);', content)
    if m:
        content = content[:m.start()] + new_foreach + content[m.end():]
        print('Enhanced slides.forEach loop with slide guards!')
    else:
        print('slides.forEach regex not matched, checking if already updated')

    # 4. Save to public/index.html
    with open('projects/dad-birthday-studio/public/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Wrote projects/dad-birthday-studio/public/index.html')

    # 5. Save to root index.html
    with open('projects/dad-birthday-studio/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Wrote projects/dad-birthday-studio/index.html')

if __name__ == '__main__':
    update_studio_html()
