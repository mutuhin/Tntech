import asyncio
from playwright.async_api import async_playwright, TimeoutError
import pandas as pd
import re

# Function for retrying page.goto
async def safe_goto(page, url, retries=3):
    for i in range(retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return  # Success
        except TimeoutError:
            if i < retries - 1:
                print(f"Retrying ({i+1}/{retries})...")
                await asyncio.sleep(2)  # Wait before retrying
            else:
                raise  # Raise the error if all retries fail


async def scrape_joint_commission():
    url = "https://www.jointcommission.org/who-we-are/who-we-work-with/find-accredited-organizations#numberOfResults=25&f:Services=[Durable%20Medical%20Equipment]"
    data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Use retry logic to navigate to the page
        await safe_goto(page, url)

        while True:
            # Wait for results to load
            await page.wait_for_selector("div.CoveoResult")

            # Scrape elements dynamically to ensure we get all required fields
            results = await page.query_selector_all("div.CoveoResult")

            for result in results:
                # Extract Title
                title_element = await result.query_selector("div.search-title > span")
                title = await title_element.inner_text() if title_element else ""

                # Extract HCO ID
                hco_id_element = await result.query_selector(
                    "div.coveo-with-label[data-field='@jcapiorganizationid'] > span:last-child"
                )
                hco_id = await hco_id_element.inner_text() if hco_id_element else ""

                # Extract Full Address
                full_address_element = await result.query_selector("div.coveo-result-address")
                full_address = await full_address_element.inner_text() if full_address_element else ""

                # Parse Full Address into components
                street_address, city, state, zip_code = "", "", "", ""
                if full_address:
                    # Split the address into lines
                    address_lines = full_address.splitlines()

                    # Assign the first line as Street Address
                    street_address = address_lines[0].strip()

                    # Process the last line for City, State, and ZIP
                    if len(address_lines) > 1:
                        last_line = address_lines[-1].strip()
                        if "," in last_line:
                            city_state_zip = last_line.split(",", 1)
                            city = city_state_zip[0].strip()

                            # Extract State and ZIP
                            state_zip_match = re.search(r"([A-Za-z]+)\s+([\d-]+)$", city_state_zip[1].strip())
                            if state_zip_match:
                                state = state_zip_match.group(1).strip()
                                zip_code = state_zip_match.group(2).strip()

                # Extract Other Addresses
                # Extract Other Addresses
                other_addresses_elements = await result.query_selector_all("div.sitedetails-location div.siteaddress")
                other_addresses = []

                # Loop through all matching elements and extract text
                for element in other_addresses_elements:
                    text = await element.inner_text()
                    other_addresses.append(text.strip())

                # Join the collected addresses into a single string (or process as needed)
                other_addresses_combined = "\n".join(other_addresses)


                # Extract Accreditation Programs
                accredited_programs_elements = await result.query_selector_all(
                    "div[id*='accordion'] tr td div.item1"
                )
                accredited_programs = [
                    await element.inner_text() for element in accredited_programs_elements
                ]

                # Extract Accreditation Decisions
                decisions_elements = await result.query_selector_all(
                    "div[id*='accordion'] tr td div.item2"
                )
                decisions = [await element.inner_text() for element in decisions_elements]

                # Extract Effective Dates
                effective_dates_elements = await result.query_selector_all(
                    "div[id*='accordion'] tr td div.item3"
                )
                effective_dates = [
                    await element.inner_text() for element in effective_dates_elements
                ]

                # Extract Last Full Survey Dates
                last_full_survey_elements = await result.query_selector_all(
                    "div[id*='accordion'] tr td div.item4"
                )
                last_full_survey_dates = [
                    await element.inner_text() for element in last_full_survey_elements
                ]

                # Extract Last On-Site Survey Dates
                last_on_site_survey_elements = await result.query_selector_all(
                    "div[id*='accordion'] tr td div.item5"
                )
                last_on_site_survey_dates = [
                    await element.inner_text() for element in last_on_site_survey_elements
                ]

                # Append data
                data.append(
                    {
                        "Title": title.strip(),
                        "All_Category": "Home Care, Durable Medical Equipment",
                        "HCO": hco_id.strip(),
                        "Full Address": full_address.strip(),
                        "Street Address": street_address.strip(),
                        "City": city.strip(),
                        "State": state.strip(),
                        "ZIP": zip_code.strip(),
                        "Other Addresses": other_addresses_combined.strip(),
                        "Accreditation Programs": ", ".join(accredited_programs),
                        "Accreditation Decision": ", ".join(decisions),
                        "Effective Date": ", ".join(effective_dates),
                        "Last Full Survey Date": ", ".join(last_full_survey_dates),
                        "Last On-Site Survey Date": ", ".join(last_on_site_survey_dates),
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


# Run the script
asyncio.run(scrape_joint_commission())
