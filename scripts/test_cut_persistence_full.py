import asyncio
import http.server
import socketserver
import threading
import os
import time
import json
from playwright.async_api import async_playwright

PORT = 8921
DIRECTORY = os.path.abspath('public')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            httpd.serve_forever()
    except Exception as e:
        print("Server exception:", e)

async def test_full_cut_persistence():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        print("\n=== STEP 1: Initial Page Load ===")
        await page.goto(f'http://127.0.0.1:{PORT}/index.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)

        # Find blessing slide
        blessing_idx = await page.evaluate('''() => {
            return slides.findIndex(s => s.cut_presets && s.primary_item?.filename?.includes('blessing_01'));
        }''')
        print(f"Blessing 1 index: {blessing_idx}")
        assert blessing_idx >= 0, "Blessing slide not found!"

        # Select slide
        await page.evaluate(f"() => selectSlide({blessing_idx})")
        await page.wait_for_timeout(500)

        init_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration,
                has_presets: !!s.cut_presets
            }};
        }}''')
        print("Initial blessing slide info:", init_info)
        assert init_info['has_presets'] == True, "Preset missing!"

        print("\n=== STEP 2: Switch to 'none' (Full raw video) ===")
        await page.click('#btn-cut-mode-none')
        await page.wait_for_timeout(500)

        none_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration,
                v9_saved: !!localStorage.getItem('dad_cloud_studio_state_v9')
            }};
        }}''')
        print("After switching to 'none':", none_info)
        assert none_info['cut_mode'] == 'none', "cut_mode should be none"
        assert 'blessing_01_raw.mp4' in none_info['url'], "URL should point to raw video"
        assert none_info['v9_saved'] == True, "State should be in v9"

        print("\n=== STEP 3: Reload Page and Verify Persistence of 'none' ===")
        await page.reload()
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)

        reload_none_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration
            }};
        }}''')
        print("After reload, blessing slide info:", reload_none_info)
        assert reload_none_info['cut_mode'] == 'none', "cut_mode must persist after reload!"
        assert 'blessing_01_raw.mp4' in reload_none_info['url'], "URL must remain raw after reload!"

        print("\n=== STEP 4: Switch to 'aggressive' (Tight cuts) ===")
        await page.evaluate(f"() => selectSlide({blessing_idx})")
        await page.wait_for_timeout(300)
        await page.click('#btn-cut-mode-aggressive')
        await page.wait_for_timeout(500)

        aggr_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration
            }};
        }}''')
        print("After switching to 'aggressive':", aggr_info)
        assert aggr_info['cut_mode'] == 'aggressive', "cut_mode should be aggressive"
        assert 'blessing_01_aggressive.mp4' in aggr_info['url'], "URL should point to aggressive video"

        print("\n=== STEP 5: Reload Page and Verify Persistence of 'aggressive' ===")
        await page.reload()
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)

        reload_aggr_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration
            }};
        }}''')
        print("After reload, blessing slide info:", reload_aggr_info)
        assert reload_aggr_info['cut_mode'] == 'aggressive', "cut_mode aggressive must persist after reload!"
        assert 'blessing_01_aggressive.mp4' in reload_aggr_info['url'], "URL must remain aggressive after reload!"

        print("\n=== STEP 6: Test Reset Video Cuts Button ===")
        await page.evaluate(f"() => selectSlide({blessing_idx})")
        await page.wait_for_timeout(300)
        await page.evaluate("() => resetVideoTrim()")
        await page.wait_for_timeout(500)

        reset_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url,
                filename: s.primary_item?.filename,
                duration: s.duration
            }};
        }}''')
        print("After resetVideoTrim():", reset_info)
        assert reset_info['cut_mode'] == 'none', "reset must set cut_mode to none"
        assert 'blessing_01_raw.mp4' in reset_info['url'], "reset must restore raw video"

        print("\n=== STEP 7: Test Migration from stale v8 cache ===")
        # Inject old v8 cache with NO cut_presets and remove v9
        from subprocess import check_output
        raw_old = check_output(['git', 'show', '298efb5:public/storyboard.json']).decode('utf-8')
        old_slides = json.loads(raw_old)['slides']

        await page.evaluate(f'''() => {{
            localStorage.removeItem('dad_cloud_studio_state_v9');
            localStorage.setItem('dad_cloud_studio_state_v8', JSON.stringify({json.dumps(old_slides)}));
            localStorage.setItem('dad_cloud_studio_last_save', '2026-09-29T15:00:00.000Z');
        }}''')

        await page.reload()
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)

        migrated_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                has_v9: !!localStorage.getItem('dad_cloud_studio_state_v9'),
                has_presets: !!s.cut_presets,
                cut_mode: s.cut_mode,
                url: s.primary_item?.url
            }};
        }}''')
        print("After v8 migration:", migrated_info)
        assert migrated_info['has_presets'] == True, "Presets must be attached during migration!"
        assert migrated_info['cut_mode'] is not None, "cut_mode must be initialized during migration!"
        assert migrated_info['has_v9'] == True, "state_v9 must be created immediately on migration!"

        # Now test that switching works on the migrated slide!
        await page.evaluate(f"() => selectSlide({blessing_idx})")
        await page.wait_for_timeout(300)
        await page.click('#btn-cut-mode-none')
        await page.wait_for_timeout(500)

        migrated_click_info = await page.evaluate(f'''() => {{
            const s = slides[{blessing_idx}];
            return {{
                cut_mode: s.cut_mode,
                url: s.primary_item?.url
            }};
        }}''')
        print("After clicking none on migrated slide:", migrated_click_info)
        assert migrated_click_info['cut_mode'] == 'none', "Must be able to click cut mode on migrated slide!"
        assert 'blessing_01_raw.mp4' in migrated_click_info['url'], "Must switch to raw video!"

        print("\n[SUCCESS] ALL CUT PERSISTENCE AND MIGRATION TESTS PASSED 100%!")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_full_cut_persistence())
