import time
from selenium import webdriver
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import numpy as np

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the barchart website
driver.get("https://www.barchart.com/futures")


# Set a timeout for page load
driver.set_page_load_timeout(10)


# JavaScript query to extract table headers
header_js_query = """
const shadowHost = document.querySelector('bc-data-grid');
const shadowRoot = shadowHost.shadowRoot;
const grid = shadowRoot.querySelector('#_grid');

const rows = Array.from(grid.querySelectorAll('div[role="row"]')).map(row => {
    return Array.from(row.querySelectorAll('div[role="columnheader"], div[role="gridcell"]'))
        .map(cell => cell.innerText.trim() || 'Empty');
});

return rows;
"""

# Execute JS to get headers
header_table_data = driver.execute_script(header_js_query)
#print("Header Table Data:", header_table_data)


# Extract column headers from the first row
headers = header_table_data[0]



# JavaScript query to extract data rows
js_query1 = """
function getData() {
    const rows = Array
        .from(document.querySelector("bc-data-grid").shadowRoot.querySelector("._grid").querySelectorAll("set-class.row"))
        .map(setClass => {
            return Array
                .from(setClass.children)
                .map(cell => {
                    const tb = cell.querySelector("text-binding");
                    return tb ? tb.shadowRoot.innerHTML : ''; // Handle null case
                });
        });

    return rows;
}
return getData();
"""
# Execute JS to get data
table_data = driver.execute_script(js_query1)
#print("Table Data:", table_data)

# Convert the data into a pandas DataFrame
df = pd.DataFrame(table_data, columns=headers)

#print("Initial DataFrame:\n", df.head())



# Clean the data: convert columns to numeric
for col in ['Last', 'Change', 'High', 'Low']:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col].str.rstrip('s').str.replace(',', '', regex=True), errors='coerce'
        )

# Drop rows with missing values
df = df.dropna(subset=['Last', 'Change', 'High', 'Low'])

# Check if DataFrame is empty after cleaning
if df.empty:
    print("DataFrame is empty after cleaning. Ensure data is being scraped correctly.")


else:
    # Calculate the mean of High and Low values
    df['Mean'] = (df['High'] + df['Low']) / 2
    offset_high = 0.1 * df['High'].max()  
    offset_low = 0.1 * df['Low'].max()  
    offset_mean = 0.1 * df['Mean'].max()
    # Plot the data
    plt.figure(figsize=(16, 8))
    plt.plot(
        df['Contract Name'],
        df['High'] + offset_high,
        label='High',
        marker='o', 
        color='blue', 
        linewidth=3, 
        markersize=8, 
        linestyle='-', 
        alpha=0.8 
    )
    plt.plot(
        df['Contract Name'],
        df['Low'] + offset_low,  
        label='Low',
        marker='^',
        color='orange',
        linewidth=3, 
        markersize=8, 
        linestyle='--',
        alpha=0.8
    )

    plt.plot(
        df['Contract Name'],
        df['Mean'] + offset_mean,
        label='Mean',
        marker='s',
        color='green', 
        linewidth=3, 
        markersize=8, 
        linestyle='-.', 
        alpha=0.8
    )
    # Set plot limits, title, and labels
    
    plt.ylim(-20000, 100000)

    plt.xlim(-0.5, len(df['Contract Name']) - 0.5)

    plt.title('High, Low, and Mean Values')
    plt.xlabel('Contract Name')
    plt.ylabel('Values')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.show()
    # Identify and print the contract with the largest change
    max_change_row = df.loc[df['Change'].idxmax()]
    contract_name = max_change_row['Contract Name']
    last_value = max_change_row['Last']
    print(f"Contract Name with largest Change: {contract_name}")
    print(f"Last Value: {last_value}")

# Save the cleaned and analyzed data to an Excel file
output_path = "\scrapping and plot\Scrap_and_plot\data_analysis.xlsx"
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Raw Data', index=False)

print(f"Data saved to {output_path}")

# Close the WebDriver

driver.quit()
