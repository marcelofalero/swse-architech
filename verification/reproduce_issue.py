from playwright.sync_api import sync_playwright, expect
import time

def run(page):
    page.goto("http://localhost:3000")

    # Wait for app to load
    page.wait_for_selector(".q-page")

    # 1. Open Add Component Dialog
    page.locator("button .q-icon").filter(has_text="add").click()

    # 2. Select Category: Weapon Systems
    page.get_by_label("Category").click()
    page.get_by_role("option", name="Weapon Systems").click()

    # 3. Select Group: Ion Weapons
    page.get_by_label("System Type").click()
    page.get_by_role("option", name="Ion Weapons").click()

    # 4. Open Component Dropdown
    page.get_by_label("Component", exact=True).click()

    # 5. Check for "Invalid Size" text in the option "Heavy Ion Cannon"
    # Heavy Ion Cannon option
    option = page.get_by_role("option", name="Heavy Ion Cannon").first
    option.wait_for()

    print(f"Option text: '{option.inner_text()}'")
    print(f"Option HTML: '{option.inner_html()}'")

    # Check if warning icon is present
    # q-icon renders as <i ...>icon_name</i>
    if "warning" in option.inner_html():
        print("Found 'warning' text/icon in HTML.")
    else:
        print("Did NOT find 'warning' in HTML.")

    page.screenshot(path="verification/repro_dropdown_debug.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        try:
            run(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
