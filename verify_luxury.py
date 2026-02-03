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

        # Create a new ship: Light Fighter (Base Cost 30,000)
        page.click("text=New Ship")
        page.click("div.q-item:has-text('Light Fighter')")

        # Base Cost Check
        # In Ledger.
        # "Total 30,000 cr" (assuming no stock modifications cost? Light Fighter has engine_5 which is stock)
        # Actually Light Fighter stock cost is 30,000.
        # Let's verify base cost.

        # Install Luxury Upgrade (Basic)
        # Cost should be 10% of hull cost.
        # Hull cost for Light Fighter (Huge) is 30,000.
        # Basic Luxury should cost 3,000.
        # Total cost should be 33,000 + fees?
        # Licensed availability fee is 5%.
        # 3000 * 0.05 = 150.
        # Total Increase: 3150.

        page.click("button.bg-positive")
        page.wait_for_selector("text=Install System")
        page.wait_for_timeout(500)

        page.click(".q-field:has-text('Category')")
        page.click("div.q-item__label:has-text('Starship Accessories')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('System Type')")
        page.click("div.q-item__label:has-text('Accommodations')")

        page.wait_for_timeout(500)
        page.click(".q-field:has-text('Component')")
        page.click("div.q-item__label:has-text('Luxury Upgrade (Basic)')")

        # Check Preview Cost if visible
        # It might show "Variable" or the calculated cost.
        # The logic in `js/app.js` uses `shipStore.getComponentCost`.
        # So it should show 3,000 cr.

        # Wait for calculation
        page.wait_for_timeout(500)

        # Check cost in dialog
        if page.locator("text=3,000 cr").count() > 0:
             print("SUCCESS: Preview Cost Correct (3,000 cr)")
        else:
             print("FAILURE: Preview Cost Incorrect")
             print(page.locator(".q-card__section").inner_text())

        page.click("button:has-text('Install')")

        # Verify Total Cost
        # 30,000 (Base) + 3,000 (Luxury) + 150 (Fee) = 33,150.

        page.wait_for_timeout(500)
        # Ledger is in ConfigPanel (Right Drawer).
        # On desktop it's always open.

        ledger_text = page.locator("div.text-h6:has-text('Total')").inner_text()
        print(f"Total Cost Displayed: {ledger_text}")

        if "33,150" in ledger_text:
            print("SUCCESS: Total Cost Verified")
        else:
            print("FAILURE: Total Cost Mismatch")

    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="error_luxury.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
