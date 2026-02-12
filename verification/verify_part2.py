import time
import os
import subprocess
import sys
from playwright.sync_api import sync_playwright

def verify_changes():
    # Start server
    server_process = subprocess.Popen([sys.executable, "-m", "http.server", "8000"], cwd=os.getcwd())
    time.sleep(2) # Give it a moment to start

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1280, 'height': 720})
            page = context.new_page()

            # Navigate to app
            page.goto("http://localhost:8000/public/swse/")

            # Bypass tutorial
            page.evaluate("localStorage.setItem('swse_tutorial_completed', 'true')")
            page.reload()

            # Wait for app to load
            page.wait_for_selector(".q-page", state="visible")
            time.sleep(1)

            # Check for Crew Quality in Config Panel
            print("Checking Crew Quality in Config Panel...")
            page.wait_for_selector("#tour-config-panel")

            if page.get_by_text("Crew Quality").is_visible():
                print("PASS: 'Crew Quality' selector found.")
            else:
                print("FAIL: 'Crew Quality' selector NOT found.")

            # Check Custom Ship Dialog for CL
            print("Checking CL in Custom Ship Dialog...")
            page.get_by_role("button", name="Custom Lib").click()
            page.wait_for_selector("div.text-h6:has-text('Library Manager')")

            if page.get_by_role("button", name="New Library").is_visible():
                 page.get_by_role("button", name="New Library").click()
                 time.sleep(0.5)

            page.locator(".q-expansion-item__toggle-icon").first.click()
            time.sleep(0.5)

            page.locator("button:has-text('New Ship'):not(#tour-hangar-btn)").click()
            page.wait_for_selector("div.text-h6:has-text('Create Custom Ship')")

            # Check for CL input - use exact label matching or handle ambiguity
            # "CL" might partially match "Ship Class" which contains "Cl"
            # Using exact match for text
            # Or use type="number" to disambiguate
            if page.locator("input[aria-label='CL']").is_visible():
                print("PASS: 'CL' input found in Custom Ship Dialog.")
            else:
                print("FAIL: 'CL' input NOT found in Custom Ship Dialog.")

            # Take screenshot
            page.screenshot(path="verification/verification_part2.png")
            print("Screenshot taken: verification/verification_part2.png")

    except Exception as e:
        print(f"Error during verification: {e}")
        try:
            page.screenshot(path="verification/error_screenshot_part2.png")
        except:
            pass
    finally:
        server_process.terminate()

if __name__ == "__main__":
    verify_changes()
