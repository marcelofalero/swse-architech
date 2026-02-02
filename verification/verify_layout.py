from playwright.sync_api import sync_playwright, expect
import time

def run(page):
    page.goto("http://localhost:3000")

    # Wait for app to load
    page.wait_for_selector(".q-page")

    # Wait for drawers to be visible
    # Drawers usually have class .q-drawer
    page.locator(".q-drawer").first.wait_for()

    time.sleep(1) # Let animations finish

    # Screenshot full desktop layout
    page.screenshot(path="verification/layout_desktop.png")

    # Check that we have 2 drawers and one page content area
    drawers = page.locator(".q-drawer").count()
    print(f"Number of drawers found: {drawers}")

    # Check center content width/presence
    # The center card should be inside q-page container
    # We can check if it is wider than the previous column layout?
    # Previously col-6 (50%), now it should take remaining space.
    # We can just visually inspect the screenshot.

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        try:
            run(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
