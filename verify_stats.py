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

        # Install Sensor Array Computer (+2 Int)
        page.click("button.bg-positive")
        page.wait_for_selector("text=Install System")
        page.wait_for_timeout(500)

        # Filter Categories to make list shorter
        page.click(".q-field:has-text('Category')")
        page.click("div.q-item__label:has-text('Starship Accessories')")
        page.wait_for_timeout(500)

        page.click(".q-field:has-text('System Type')")
        page.click("div.q-item__label:has-text('Computers')")
        page.wait_for_timeout(500)

        # Select
        page.click(".q-field:has-text('Component')")
        page.click("div.q-item__label:has-text('Sensor Array Computer (+2 Int)')")

        page.click("button:has-text('Install')")

        # Check Stats
        page.wait_for_timeout(500)

        # The StatPanel is on the left.
        # Structure: col-4 -> bg-grey-8 -> div (Label) + div (Value)
        # We can target by text.

        # Find element containing "INT" and get its sibling or child with value.
        # The template has: <div>{{ $t('stats.int') }}</div><div class="text-bold">{{ store.currentStats.int }}</div>

        # Locate the container of INT
        int_container = page.locator("div.bg-grey-8:has-text('INT')")
        int_text = int_container.locator(".text-bold").inner_text()

        print(f"Int Value: {int_text}")

        if int_text == "16":
            print("SUCCESS: Int Bonus Verified")
        else:
            print(f"FAILURE: Int Bonus Mismatch (Expected 16, Got '{int_text}')")

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="error_sensor_3.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
