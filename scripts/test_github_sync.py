import asyncio
import http.server
import socketserver
import threading
import os
import time
import subprocess
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

PORT = 8792
DIRECTORY = os.path.abspath('projects/dad-birthday-studio/public')

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

async def main():
    # Start local static server
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    gh_token = subprocess.check_output(['gh', 'auth', 'token']).decode().strip()
    print("Obtained local gh token successfully (prefix:", gh_token[:7] + "...)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1400, 'height': 900})
        page = await context.new_page()

        # Handle dialogs automatically (alert, confirm)
        dialog_messages = []
        page.on("dialog", lambda dialog: (dialog_messages.append(dialog.message), asyncio.create_task(dialog.accept())))
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))

        await page.goto(f'http://127.0.0.1:{PORT}/index.html')
        await page.wait_for_load_state('networkidle')

        print("=== Test 1: Clicking save without token opens modal ===")
        # Clear any token
        await page.evaluate("() => localStorage.removeItem('dad_studio_github_token')")
        
        # Click save button
        await page.click("button.gold:has-text('שמור בענן')")
        await page.wait_for_timeout(500)

        modal_visible = await page.is_visible("#github-token-modal")
        print("Modal visible without token:", modal_visible)
        await page.screenshot(path="C:/Users/guyco/.gemini/antigravity/brain/8ffd9814-0a57-4ac8-bb60-3d91aaa37bf3/test_github_modal.png")

        print("=== Test 2: Enter token and sync to GitHub ===")
        # Fill token into input
        await page.fill("#modal-gh-token-input", gh_token)
        
        # Click modal save button
        await page.click("#github-token-modal button.gold")
        
        # Wait for API sync to complete
        await page.wait_for_timeout(4000)

        status_text = await page.evaluate("() => document.getElementById('cloud-sync-status').textContent")
        print("Cloud Sync Status after sync:", status_text)
        print("Dialog messages captured:", dialog_messages)

        await page.screenshot(path="C:/Users/guyco/.gemini/antigravity/brain/8ffd9814-0a57-4ac8-bb60-3d91aaa37bf3/test_github_sync_success.png")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
