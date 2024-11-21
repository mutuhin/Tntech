from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_linkedin():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()

        page.goto("https://www.linkedin.com/login")

        page.fill('input[name="session_key"]', 'tuhinmh362@gmail.com')  
        page.fill('input[name="session_password"]', '******')  
        page.click('button[type="submit"]')  

        page.wait_for_timeout(3000) 

        profile_url = "https://www.linkedin.com/in/tuhin-mh-30208a339/"
        page.goto(profile_url)

        name = page.inner_text('h1.text-heading-xlarge')
        headline = page.inner_text('div.text-body-medium')
        location = page.inner_text('span.text-body-small')

        print(f"Name: {name}")
        print(f"Headline: {headline}")
        print(f"Location: {location}")

        data = {
            "Name": [name],
            "Headline": [headline],
            "Location": [location],
        }

        df = pd.DataFrame(data)
        df.to_csv("linkedin_profiles.csv", index=False)

        browser.close()

if __name__ == "__main__":
    scrape_linkedin()
