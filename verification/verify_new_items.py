from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:8080")

    # Wait for app to load
    page.wait_for_selector("#q-app")

    # Click Add Component button
    page.locator("button:has(.q-icon:text('add'))").first.click()

    # Wait for dialog
    expect(page.locator(".q-dialog")).to_be_visible()

    # Select Category: Defense Systems
    # "Category" is the first select.
    # We use .first to pick the "Category" field and avoid the "System Type" field which has 'category' icon text.
    page.locator(".q-field").filter(has_text="Category").first.click()
    # Wait for options. They are in .q-menu
    page.get_by_role("option", name="Defense Systems").click()

    # Select Group: Armor
    # "System Type"
    page.locator(".q-field").filter(has_text="System Type").click()
    page.get_by_role("option", name="Armor").click()

    # Open Component list
    page.locator(".q-field").filter(has_text="Component").click()

    # Verify new armor exists
    expect(page.get_by_role("option", name="Starship Armor (+4)")).to_be_visible()

    # Close component list
    page.locator("body").press("Escape")
    page.wait_for_timeout(500)

    # Change Group to Shield Generators
    # Click System Type again.
    page.locator(".q-field").filter(has_text="System Type").click()
    page.get_by_role("option", name="Shield Generators").click()

    # Open Component list
    page.locator(".q-field").filter(has_text="Component").click()

    # Verify new shields exist
    # Since there are many shields, we might need to scroll or type.
    # But let's check if it's in the DOM.
    # If not visible, we might need to scroll.
    # I'll force scroll or check existence.
    # For now, check visibility. If it fails, I'll assume I need to scroll.
    # But standard select options are usually all rendered in QMenu or virtual scroll.
    # If virtual scroll, I might not see it.
    # But let's try.
    shield_option = page.get_by_role("option", name="Shield Generator (SR 200)")
    if shield_option.count() > 0:
        shield_option.scroll_into_view_if_needed()
    expect(shield_option).to_be_visible()

    # Take screenshot of Shields list
    page.screenshot(path="verification/shields_list.png")

    print("Verification successful!")

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as p:
        run(p)
