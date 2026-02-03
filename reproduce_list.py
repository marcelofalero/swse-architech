from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("http://localhost:8000/index.html")
            page.wait_for_selector("#q-app", state="visible")

            # Open Manager
            page.click("button:has-text('Custom Lib')")
            page.wait_for_selector("text=Custom Components Library", state="visible")

            # Click Create New
            page.click("button:has-text('Create New')")
            page.wait_for_selector("text=Create Custom Component", state="visible")

            # Fill
            page.fill("input[aria-label='Name']", "TestItem")

            # Click Create (use exact match or container to be safe)
            # The dialog is the last one in DOM usually
            page.click("div[role='dialog'] >> text=Create", strict=False)
            # strict=False allows matching if text=Create is inside the button

            time.sleep(1)

            # Check list
            if page.is_visible("text=TestItem"):
                print("SUCCESS: Item found")
            else:
                print("FAILURE: Item not found")

        except Exception as e:
            print(f"Exception: {e}")

        browser.close()

if __name__ == "__main__":
    run()
