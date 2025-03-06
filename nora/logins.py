'''
 # @ Create Time: 2024-07-05 14:47:20
 # @ Modified time: 2024-08-21 10:46:00
 # @ Description: simulate the login on host web service
'''

from playwright.sync_api import sync_playwright

def login_playwright(username: str, password: str, url: str = "https://possible-concrete-constellation.glitch.me/login.html"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        page.fill("#username", username)
        page.fill("#password", password)
        page.click("button")

        try:
            page.wait_for_url("**/dashboard.html", timeout=5000)  # 5 seconds timeout
            success = "dashboard.html" in page.url
        except TimeoutError:
            success = False  # Login failed or page didn't redirect

        browser.close()
        return success

# Example usage
if login_playwright("admin", "password"):
    print("Login successful!")
else:
    print("Login failed!")
