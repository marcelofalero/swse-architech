import json
import urllib.request
import urllib.error
import time
import os

DATA_FILE = 'public/swse/data.json'
REPORT_FILE = 'missing_miraheze_pages.txt'

def check_url(url):
    try:
        # Use a proper User-Agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        req = urllib.request.Request(url, method='HEAD', headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, "OK"
    except urllib.error.HTTPError as e:
        if e.code == 405: # Method Not Allowed, try GET
            try:
                req = urllib.request.Request(url, method='GET', headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.status, "OK"
            except urllib.error.HTTPError as e2:
                return e2.code, e2.reason
            except Exception as e2:
                return 0, str(e2)
        return e.code, e.reason
    except Exception as e:
        return 0, str(e)

def main():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return

    updated_count = 0
    total_checks = 0
    missing_components = []
    unverified_components = []

    # Process EQUIPMENT list
    if 'EQUIPMENT' in data:
        for item in data['EQUIPMENT']:
            if 'wiki' in item:
                old_url = item['wiki']
                # Check for fandom.com or fandom.org
                if 'swse.fandom.com' in old_url or 'swse.fandom.org' in old_url:
                    # Construct new URL
                    new_url = old_url.replace('swse.fandom.com', 'swse.miraheze.org')
                    new_url = new_url.replace('swse.fandom.org', 'swse.miraheze.org')

                    print(f"Checking {item.get('name', 'Unknown')}: {new_url}...")

                    status, reason = check_url(new_url)

                    if status == 200:
                        item['wiki'] = new_url
                        updated_count += 1
                        print(f"  -> VALID (200). Updated.")
                    elif status == 404:
                         print(f"  -> MISSING (404). Keeping old URL.")
                         missing_components.append({
                            'name': item.get('name', 'Unknown'),
                            'id': item.get('id', 'unknown'),
                            'old_url': old_url,
                            'new_url': new_url,
                            'error': "404 Not Found"
                        })
                    else:
                        # 403, 0 (Connection Error), etc.
                        # We assume these are valid but blocked, or site issues.
                        # We will MIGRATE them but report as Unverified.
                        print(f"  -> UNVERIFIED ({status} {reason}). Updating anyway.")
                        item['wiki'] = new_url
                        updated_count += 1
                        unverified_components.append({
                            'name': item.get('name', 'Unknown'),
                            'id': item.get('id', 'unknown'),
                            'old_url': old_url,
                            'new_url': new_url,
                            'error': f"{status} {reason}"
                        })

                    total_checks += 1
                    time.sleep(0.2) # Faster since we are blocked anyway

    # Save updated JSON if changes were made
    if updated_count > 0:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nUpdate complete. {updated_count} URLs updated out of {total_checks} checked.")
    else:
        print(f"\nNo URLs were updated (checked {total_checks}).")

    # Generate report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("Migration Report\n================\n\n")

        if missing_components:
            f.write(f"MISSING COMPONENTS ({len(missing_components)}) - Not Updated:\n")
            for missing in missing_components:
                f.write(f"- {missing['name']} (ID: {missing['id']})\n")
                f.write(f"  Old: {missing['old_url']}\n")
                f.write(f"  New: {missing['new_url']}\n")
                f.write(f"  Error: {missing['error']}\n\n")

        if unverified_components:
            f.write(f"UNVERIFIED COMPONENTS ({len(unverified_components)}) - Updated (Network/Block Issue):\n")
            for unv in unverified_components:
                f.write(f"- {unv['name']} (ID: {unv['id']})\n")
                f.write(f"  New: {unv['new_url']}\n")
                f.write(f"  Error: {unv['error']}\n\n")

    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
