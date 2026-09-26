import asyncio
import http.server
import socketserver
import threading
import os
import time
from playwright.async_api import async_playwright

PORT = 8792
DIRECTORY = os.path.abspath('projects/dad-birthday-studio/public')

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

async def test_zoom_persistence():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        await page.goto(f'http://127.0.0.1:{PORT}/index.html')
        await page.wait_for_load_state('networkidle')

        print("--- 1. Select Slide 3 (index 2: 260_IMG-20260827-WA0024.jpg) ---")
        await page.evaluate("() => selectSlide(2)")
        await page.wait_for_timeout(500)

        initial_state = await page.evaluate("""() => {
            const cur = slides[2];
            return {
                id: cur.slide_id,
                filename: cur.primary_item.filename,
                scale: cur.scale,
                offsetX: cur.offsetX,
                offsetY: cur.offsetY
            };
        }""")
        print("Initial Slide 3 state:", initial_state)

        print("--- 2. Apply Custom Zoom & Offsets to Slide 3 ---")
        # Update scale to 1.95, offsetY to -45, offsetX to 30
        await page.evaluate("""() => {
            updateCurrentScale(1.95);
            updateCurrentOffsetY(-45);
            updateCurrentOffsetX(30);
            autoSaveState();
        }""")
        await page.wait_for_timeout(500)

        mid_state = await page.evaluate("""() => {
            const cur = slides[2];
            return {
                scale: cur.scale,
                offsetX: cur.offsetX,
                offsetY: cur.offsetY,
                valScale: document.getElementById('val-scale').textContent,
                valOffsetY: document.getElementById('val-offsetY').textContent,
                valOffsetX: document.getElementById('val-offsetX').textContent
            };
        }""")
        print("Modified Slide 3 state before reload:", mid_state)
        await page.screenshot(path="projects/dad-birthday-studio/debug_slide_3_zoomed.png")

        print("--- 3. Reload Page and Verify State Persistence ---")
        await page.reload()
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(500)

        # Select slide 2 again
        await page.evaluate("() => selectSlide(2)")
        await page.wait_for_timeout(500)

        after_reload_state = await page.evaluate("""() => {
            const cur = slides[2];
            return {
                id: cur.slide_id,
                filename: cur.primary_item.filename,
                scale: cur.scale,
                offsetX: cur.offsetX,
                offsetY: cur.offsetY,
                valScale: document.getElementById('val-scale').textContent,
                valOffsetY: document.getElementById('val-offsetY').textContent,
                valOffsetX: document.getElementById('val-offsetX').textContent
            };
        }""")
        print("Slide 3 state AFTER page reload:", after_reload_state)
        await page.screenshot(path="projects/dad-birthday-studio/debug_slide_3_after_reload.png")

        # Assertions
        assert after_reload_state['scale'] == 1.95, f"Expected scale 1.95 but got {after_reload_state['scale']}"
        assert after_reload_state['offsetY'] == -45, f"Expected offsetY -45 but got {after_reload_state['offsetY']}"
        assert after_reload_state['offsetX'] == 30, f"Expected offsetX 30 but got {after_reload_state['offsetX']}"
        print(">>> SUCCESS: Slide 3 custom zoom and pan persisted across page reload!")

        print("--- 4. Verify Slide 2 (index 1: 259_) Persistence ---")
        await page.evaluate("() => selectSlide(1)")
        await page.evaluate("""() => {
            updateCurrentScale(1.8);
            updateCurrentOffsetY(25);
            autoSaveState();
        }""")
        await page.reload()
        await page.wait_for_load_state('networkidle')
        await page.evaluate("() => selectSlide(1)")
        slide1_after = await page.evaluate("""() => {
            const cur = slides[1];
            return { scale: cur.scale, offsetY: cur.offsetY };
        }""")
        print("Slide 2 after reload:", slide1_after)
        assert slide1_after['scale'] == 1.8, f"Expected scale 1.8 but got {slide1_after['scale']}"
        assert slide1_after['offsetY'] == 25, f"Expected offsetY 25 but got {slide1_after['offsetY']}"
        print(">>> SUCCESS: Slide 2 custom zoom and pan persisted across page reload!")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_zoom_persistence())