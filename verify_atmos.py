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

        # Install Atmospheric Thrusters
        page.click("button.bg-positive")
        page.wait_for_selector("text=Install System")
        page.wait_for_timeout(500)

        # Category: Movement Systems
        page.click(".q-field:has-text('Category')")
        page.click("div.q-item__label:has-text('Movement Systems')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('System Type')")
        page.click("div.q-item__label:has-text('Thrusters')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('Component')")

        # Find Atmospheric Thrusters
        page.click("div.q-item__label:has-text('Atmospheric Thrusters')")

        # Check Price and EP in Preview
        # Should be 2000 cr (Base) * SizeMult.
        # Light Fighter is Huge (SizeMult = 1).
        # Cost: 2000 cr.
        # EP: 2.

        page.wait_for_timeout(500)

        # The dialog shows cost/EP on the right.
        # We need to target the text.

        preview_card = page.locator(".q-card.bg-grey-8")
        cost_text = preview_card.locator(".text-h6.text-amber").inner_text()
        ep_text = preview_card.locator(".text-caption.text-positive").inner_text()

        print(f"Cost: {cost_text}")
        print(f"EP: {ep_text}")

        if "2,000 cr" in cost_text and "2 EP" in ep_text:
            print("SUCCESS: Atmospheric Thrusters Verified")
        else:
            print("FAILURE: Stats Mismatch")

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="error_atmos.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
