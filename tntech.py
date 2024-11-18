import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_tntech():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Initialize an empty list to store the data
        data = []

        try:
            # Step 1: Navigate to the Tennessee Tech homepage
            await page.goto("https://www.tntech.edu/", timeout=60000, wait_until="domcontentloaded")
            print("Homepage loaded successfully")

            # Step 2: Navigate to the Admissions page
            await page.get_by_role("menuitem", name="Admissions").click()
            await page.wait_for_load_state("domcontentloaded")
            print("Navigated to Admissions page")

            # Step 3: Navigate to the International Admissions page
            international_xpath = "//a[@class='blockInner' and contains(@href, '/admissions/international/index.php')]"
            await page.locator(international_xpath).click()
            await page.wait_for_load_state("domcontentloaded")
            print("Navigated to International Admissions page")

            # Step 4: Extract URLs from the blocks
            blocks_xpath = "//div[@class='grid-x grid-margin-x small-up-1 medium-up-3']//a[@class='blockInner']"
            block_elements = await page.locator(blocks_xpath).all()
            
            urls = []
            for block in block_elements:
                href = await block.get_attribute("href")
                if href:
                    full_url = f"https://www.tntech.edu{href}"
                    urls.append(full_url)
            
            print("\nExtracted URLs:")
            for url in urls:
                print(url)

            # Step 5: Visit each URL and extract data
            for url in urls:
                print(f"\nNavigating to: {url}")
                await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                # Extract the page title
                title = await page.title()
                print(f"Title: {title}")
                
                # Extract content from the first div
                content_div_locator = page.locator("//div[@class='small-12 cell eagleContent']").first

                content_text = ""
                if await content_div_locator.is_visible():
                    content_text = await content_div_locator.inner_text()
                    print("\nExtracted Content:\n")
                    print(content_text)
                else:
                    print("The content div was not found on the page.")
                
                # Add the extracted data to the list
                data.append({
                    'URL': url,
                    'Title': title,
                    'Content': content_text
                })

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

        # Convert the data list into a Pandas DataFrame
        df = pd.DataFrame(data)

        # Save the DataFrame to a CSV file
        df.to_csv('tntech_data.csv', index=False, encoding='utf-8')
        print("\nData has been saved to 'tntech_data.csv'")

# Run the script
asyncio.run(scrape_tntech())
