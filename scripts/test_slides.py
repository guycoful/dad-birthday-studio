import asyncio
import http.server
import socketserver
import threading
import os
import time
from playwright.async_api import async_playwright

PORT = 8789
DIRECTORY = os.path.abspath('projects/dad-birthday-studio/public')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

async def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()

        # Listen to console logs
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        await page.goto(f'http://127.0.0.1:{PORT}/index.html')
        await page.wait_for_load_state('networkidle')

        print("=== Checking Slide 1 (Baby - 319) ===")
        # Check current slide
        src = await page.evaluate("() => document.getElementById('main-photo').src")
        print("Slide 0 main-photo src:", src)
        await page.screenshot(path="projects/dad-birthday-studio/debug_slide_1.png")

        print("=== Selecting Slide 2 (Photo 259) ===")
        await page.evaluate("() => selectSlide(1)")
        await page.wait_for_timeout(1000)
        
        slide1_info = await page.evaluate("""() => {
            const cur = slides[1];
            return {
                caption: cur.caption,
                colorized_path: cur.colorized_path,
                scale: cur.scale,
                offsetY: cur.offsetY,
                trim: cur.trim,
                mainSrc: document.getElementById('main-photo').src,
                scaleVal: document.getElementById('val-scale').textContent,
                trimVal: document.getElementById('val-trim').textContent,
                offsetYVal: document.getElementById('val-offsetY').textContent
            };
        }""")
        print("Slide 2 info:", slide1_info)
        await page.screenshot(path="projects/dad-birthday-studio/debug_slide_2.png")

        print("=== Selecting Slide 3 (Photo 260) ===")
        await page.evaluate("() => selectSlide(2)")
        await page.wait_for_timeout(1000)
        
        slide2_info = await page.evaluate("""() => {
            const cur = slides[2];
            return {
                caption: cur.caption,
                colorized_path: cur.colorized_path,
                scale: cur.scale,
                offsetY: cur.offsetY,
                trim: cur.trim,
                mainSrc: document.getElementById('main-photo').src,
                scaleVal: document.getElementById('val-scale').textContent,
                trimVal: document.getElementById('val-trim').textContent,
                offsetYVal: document.getElementById('val-offsetY').textContent
            };
        }""")
        print("Slide 3 info:", slide2_info)
        await page.screenshot(path="projects/dad-birthday-studio/debug_slide_3.png")

        await browser.close()
        print("Test completed successfully!")

if __name__ == '__main__':
    asyncio.run(main())
