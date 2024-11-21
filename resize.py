

import pandas as pd
import re

# Load the CSV file
input_file = "/Users/mujahidulhaqtuhin/Documents/Linkedin/organizations.csv"  # Update with your file path
output_file = "/Users/mujahidulhaqtuhin/Documents/Linkedin/processed_organizations.csv"  # Update with your desired output path

# Load data
df = pd.read_csv(input_file)

# Function to extract address components
def extract_address_components(address):
    if pd.isna(address):  # Check for NaN and return empty fields
        return "", "", ""
    # Use regex to extract city, state, and ZIP
    pattern = r"^(.*?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)$"
    match = re.search(pattern, address)
    if match:
        street = match.group(1).strip()
        state = match.group(2).strip()
        zip_code = match.group(3).strip()
        return street, state, zip_code
    else:
        return address, "", ""  # Return empty state and ZIP if not found

# Apply the function to the "Street Address" column
df["Street Address"] = df["Street Address"].astype(str)  # Ensure all values are strings
df["Street Address Cleaned"], df["State"], df["ZIP"] = zip(*df["Street Address"].map(extract_address_components))

# Drop the old "Street Address" column if needed
df.rename(columns={"Street Address Cleaned": "Street Address"}, inplace=True)

# Save the processed file
df.to_csv(output_file, index=False)
print(f"Processed file saved to {output_file}")
