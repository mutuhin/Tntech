import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from lxml import html


async def scrape_joint_commission():
    url = "https://www.jointcommission.org/who-we-are/who-we-work-with/find-accredited-organizations#numberOfResults=25&f:Services=[Durable%20Medical%20Equipment]"
    data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        while True:
            await page.wait_for_selector("div.CoveoResult")

            # Scrape elements dynamically to ensure we get `full_address`
            results = await page.query_selector_all("div.CoveoResult")
            
            for result in results:
                # Extract the title
                title = await (await result.query_selector(
                    "div.search-title > span"
                )).inner_text() if await result.query_selector("div.search-title > span") else ""

                # Extract HCO ID
                hco_id_element = await result.query_selector(
                    "div.coveo-with-label[data-field='@jcapiorganizationid'] > span:last-child"
                )
                hco_id = await hco_id_element.inner_text() if hco_id_element else ""

                # Extract full address
                full_address_element = await result.query_selector("div.coveo-result-address")
                full_address = await full_address_element.inner_text() if full_address_element else ""

                # Parse full address into components
                street_address, city, state, zip_code = "", "", "", ""
                if full_address:
                    address_parts = [part.strip() for part in full_address.split(",")]
                    street_address = address_parts[0] if len(address_parts) > 0 else ""
                    city = address_parts[1] if len(address_parts) > 1 else ""
                    if len(address_parts) > 2:
                        state_zip = address_parts[2].split()
                        state = state_zip[0] if len(state_zip) > 0 else ""
                        zip_code = state_zip[1] if len(state_zip) > 1 else ""

                # Extract additional fields if necessary
                other_addresses_element = await result.query_selector("div.sitedetails-location div.siteaddress")
                other_addresses = await other_addresses_element.inner_text() if other_addresses_element else ""

                data.append(
                    {
                        "Title": title.strip(),
                        "All_Category": "Home Care, Durable Medical Equipment",
                        "HCO": hco_id.strip(),
                        "Full Address": full_address.strip(),
                        "Street Address": street_address,
                        "City": city,
                        "State": state,
                        "ZIP": zip_code,
                        "OtherAddresses": other_addresses.strip(),
                    }
                )

            # Check for the "next" button
            next_button = await page.query_selector("li.coveo-pager-next")
            if next_button:
                await next_button.click()
                await page.wait_for_timeout(3000)
            else:
                break

        await browser.close()

    # Save the data to CSV
    df = pd.DataFrame(data)
    df.to_csv("accredited_organizations.csv", index=False)
    print("Data saved to accredited_organizations.csv")


asyncio.run(scrape_joint_commission())
