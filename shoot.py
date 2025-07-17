import os
import sys
import requests
import shutil
import asyncio
from playwright.async_api import async_playwright

WEBHOOK_URL = "<Your_Discord_webhook>"
SCREENSHOT_DIR = "screenshots"

def send_to_discord(image_path, url):
    with open(image_path, "rb") as f:
        files = {"file": (os.path.basename(image_path), f)}
        payload = {"content": f"📸 Screenshot of `{url}`"}
        response = requests.post(WEBHOOK_URL, data=payload, files=files)
        if response.status_code == 204:
            print(f"[+] Sent: {image_path}")
        else:
            print(f"[-] Failed to send {image_path}: {response.status_code}")

async def take_and_send_screenshots(subdomains):
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        for sub in subdomains:
            url = f"https://{sub.strip()}"
            try:
                page = await context.new_page()
                print(f"[*] Visiting: {url}")
                await page.goto(url, timeout=15000)
                filename = os.path.join(SCREENSHOT_DIR, sub.replace('.', '_') + ".png")
                await page.screenshot(path=filename, full_page=True)
                print(f"[+] Screenshot taken: {filename}")
                await page.close()
                send_to_discord(filename, url)
                os.remove(filename)
            except Exception as e:
                print(f"[-] Failed to screenshot {url}: {e}")
        await browser.close()

def cleanup():
    if os.path.exists(SCREENSHOT_DIR):
        shutil.rmtree(SCREENSHOT_DIR)
        print("[+] Screenshot directory deleted.")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} subdomains.list")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print("[-] Subdomain list not found.")
        sys.exit(1)

    with open(file_path) as f:
        subdomains = [line.strip() for line in f if line.strip()]

    asyncio.run(take_and_send_screenshots(subdomains))
    cleanup()

if __name__ == "__main__":
    main()
