import time
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
import pandas as pd
from matplotlib.animation import FuncAnimation

# Initialize the WebDriver
driver = webdriver.Chrome()

# Open the barchart website
driver.get("https://www.barchart.com/futures")
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
header_table_data = driver.execute_script(header_js_query)

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

# Setup plot
plt.figure(figsize=(16, 8))
plt.title('High, Low, and Mean Values Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Contract Name')
plt.grid(True, linestyle='--', linewidth=0.5)

# Initialize time list and data lists
time_list = []
contract_names = []
high_values = {}
low_values = {}
mean_values = {}

# Set the animation function to update the plot
def update_plot(i):
    # Run the query every 5 seconds and extract the data
    table_data = driver.execute_script(js_query1)

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(table_data, columns=headers)

    # Clean the data: convert columns to numeric
    for col in ['Last', 'Change', 'High', 'Low']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].str.rstrip('s').str.replace(',', '', regex=True), errors='coerce')

    df = df.dropna(subset=['High', 'Low'])
    
    # Calculate the mean of High and Low values
    df['Mean'] = (df['High'] + df['Low']) / 2

    # Add the current time to the time list
    time_list.append(time.time())  # Add current time for the x-axis
    
    # Loop through each contract and plot its data
    for _, row in df.iterrows():
        contract_name = row['Contract Name']
        if contract_name not in contract_names:
            contract_names.append(contract_name)
            high_values[contract_name] = []
            low_values[contract_name] = []
            mean_values[contract_name] = []

        high_values[contract_name].append(row['High'])
        low_values[contract_name].append(row['Low'])
        mean_values[contract_name].append(row['Mean'])

    # Update the plot
    plt.cla()  # Clear the current plot
    
    # Plot data for each contract name
    for contract_name in contract_names:
        if len(high_values[contract_name]) > 0:
            plt.plot(time_list, high_values[contract_name], label=f'{contract_name} High', linestyle='-', marker='o')
            plt.plot(time_list, low_values[contract_name], label=f'{contract_name} Low', linestyle='--', marker='^')
            plt.plot(time_list, mean_values[contract_name], label=f'{contract_name} Mean', linestyle='-.', marker='s')

    plt.title('High, Low, and Mean Values Over Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Values')
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.tight_layout()

# Set the animation to update every 5 seconds
ani = FuncAnimation(plt.gcf(), update_plot, interval=5000, repeat=False, frames=4)  # Run for 20 sec, every 5 sec

plt.show()

# Close the WebDriver after the plot finishes
driver.quit()
