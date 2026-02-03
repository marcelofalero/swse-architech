from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1280, "height": 1024})
    page = context.new_page()

    try:
        # Load the app
        page.goto("http://localhost:8080")

        # Wait for app to load
        page.wait_for_selector("text=New Ship")

        # Create a new ship: Light Fighter
        page.click("text=New Ship")
        page.click("div.q-item:has-text('Light Fighter')")

        # Install Twin Light Laser Cannon
        page.click("button.bg-positive")
        page.wait_for_selector("text=Install System")
        page.wait_for_timeout(500)

        # Search
        #page.fill("input[type='search']", "Twin Light Laser") # Search input might not exist or be selectable easily
        # Use Categories
        page.click(".q-field:has-text('Category')")
        page.click("div.q-item__label:has-text('Weapon Systems')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('System Type')")
        page.click("div.q-item__label:has-text('Laser Cannons')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('Component')")
        page.click("div.q-item__label:has-text('Twin Light Laser Cannon')")

        page.click("button:has-text('Install')")

        # Open Sheet and Check Description
        page.wait_for_timeout(500)
        page.click("text=Sheet")
        page.wait_for_selector("text=Twin Light Laser Cannon")

        # Check text
        expected_text = "Can fire normally or in Autofire mode"

        if page.locator(f"text={expected_text}").count() > 0:
            print("SUCCESS: Autofire Description Verified")
        else:
            print("FAILURE: Autofire Description Missing")
            print(page.locator(".sheet-body").inner_text())

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="error_autofire.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
