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

            content = await page.content()
            tree = html.fromstring(content)

            entries = tree.xpath("//div[contains(@class, 'CoveoResult')]")

            for entry in entries:
                title = entry.xpath(".//div[contains(@class, 'search-title')]/span/text()")
                hco_id = entry.xpath(
                    ".//div[contains(@class, 'coveo-with-label') and @data-field='@jcapiorganizationid']/span[last()]/text()"
                )
                street_address_full = entry.xpath(
                    ".//div[@class='coveo-result-address']//div[contains(@data-field, '@jcapistreet')]/span/text()"
                )

                city = entry.xpath(".//div[@class='coveo-result-address']//span[contains(@data-field, '@jcapicity')]/text()")
                state_zip = entry.xpath(
                    ".//div[@class='coveo-result-address']//span[contains(@data-field, '@jcapipostalcodestring')]/text()"
                )
                state, zip_code = None, None
                if state_zip:
                    state_zip_parts = state_zip[0].strip().split()
                    state = state_zip_parts[0] if len(state_zip_parts) > 0 else None
                    zip_code = state_zip_parts[1] if len(state_zip_parts) > 1 else None

                street_address = (
                    street_address_full[0].strip() if street_address_full else ""
                )

                other_addresses = entry.xpath(
                    ".//div[@class='sitedetails-location']//div[@class='siteaddress']/text()"
                )
                accredited_programs = entry.xpath(
                    ".//div[contains(@id, 'accordion')]//tr/td/div[@class='item1']/text()"
                )
                decisions = entry.xpath(
                    ".//div[contains(@id, 'accordion')]//tr/td/div[@class='item2']/text()"
                )
                effective_dates = entry.xpath(
                    ".//div[contains(@id, 'accordion')]//tr/td/div[@class='item3']/text()"
                )
                last_full_survey_date = entry.xpath(
                    ".//div[contains(@id, 'accordion')]//tr/td/div[@class='item4']/text()"
                )
                last_on_site_survey_date = entry.xpath(
                    ".//div[contains(@id, 'accordion')]//tr/td/div[@class='item5']/text()"
                )

                data.append(
                    {
                        "Title": title[0].strip() if title else "",
                        "All_Category": "Home Care, Durable Medical Equipment",  # Customize as needed
                        "HCO": hco_id[0].strip() if hco_id else "",
                        "Street Address": street_address,
                        "City": city[0].strip() if city else "",
                        "State": state.strip() if state else "",
                        "ZIP": zip_code.strip() if zip_code else "",
                        "OtherAddresses": "\n".join(other_addresses).strip()
                        if other_addresses
                        else "",
                        "Accreditation Programs": ", ".join(accredited_programs),
                        "Accreditation Decision": ", ".join(decisions),
                        "Effective Date": ", ".join(effective_dates),
                        "Last Full Survey Date": ", ".join(last_full_survey_date),
                        "Last On-Site Survey Date": ", ".join(last_on_site_survey_date),
                    }
                )

            next_button = await page.query_selector("li.coveo-pager-next")
            if next_button:
                await next_button.click()
                await page.wait_for_timeout(3000)  
            else:
                break  

        await browser.close()

    df = pd.DataFrame(data)
    df.to_csv("accredited_organizations.csv", index=False)
    print("Data saved to accredited_organizations.csv")


asyncio.run(scrape_joint_commission())
