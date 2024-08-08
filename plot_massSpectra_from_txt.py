import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image
from io import BytesIO
import numpy as np

# Directory containing the text files
directory = r'E:\Clowers_Benzhydrylpyridinium'

# Initialize the workbook
wb = Workbook()
# Remove the default sheet created automatically by openpyxl
wb.remove(wb.active)

# Specific m/z values to label
target_mz = {
    '1-40': [430.18, 351.14],
    '1-42': [306.15, 227.11],
    '1-44': [398.19, 319.15],
    '1-46': [336.17, 257.13],
    '1-48': [322.16, 243.12],
    '1-50': [310.10, 312.10, 231.06, 233.09],
    '1-52': [354.05, 356.05, 275.01, 277.01],
    '1-54': [294.13, 215.09]
}

# Loop through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Read the data from the text file into a pandas DataFrame
        data = pd.read_csv(file_path, sep='\t')
        
        # Filter data to include only m/z <= 450
        filtered_data = data[data['Mass/Charge'] <= 450]
        
        # Create a plot
        plt.figure(figsize=(10, 6))
        plt.plot(filtered_data['Mass/Charge'], filtered_data['Intensity'], linestyle='-', color='black')
        plt.title(f'Q1 scan of {filename[:-4]}')
        plt.xlabel('m/z')
        plt.ylabel('Intensity')
        plt.grid(True)
        plt.xlim(right=600)  

        # Common peak detection for grey peaks
        peaks, _ = find_peaks(filtered_data['Intensity'], height=max(filtered_data['Intensity']) * 0.2)
        
        # Get the specific peaks to label from the dictionary
        specific_peaks = target_mz.get(filename[:-4], [])
        specific_peaks_indices = []

        # Find nearest data points to the specified m/z values
        for mz in specific_peaks:
            nearest_index = (np.abs(filtered_data['Mass/Charge'] - mz)).idxmin()
            specific_peaks_indices.append(nearest_index)
            plt.plot(filtered_data['Mass/Charge'][nearest_index], filtered_data['Intensity'][nearest_index], 'ro')
            plt.annotate(f'{filtered_data["Mass/Charge"][nearest_index]:.2f}',
                         (filtered_data['Mass/Charge'][nearest_index], filtered_data['Intensity'][nearest_index]),
                         textcoords="offset points", xytext=(0,10), ha='center', color='red', fontweight='bold')

        # Annotate common peaks
        for peak in peaks:
            if peak not in specific_peaks_indices:
                plt.annotate(f'{filtered_data["Mass/Charge"].iloc[peak]:.2f}',
                            (filtered_data['Mass/Charge'].iloc[peak], filtered_data['Intensity'].iloc[peak]),
                            textcoords="offset points", xytext=(0,10), ha='center', color='grey')

        # Save the plot to a bytes buffer
        plot_buffer = BytesIO()
        plt.savefig(plot_buffer, format='png')
        plt.close()

        # Create a worksheet for this file
        sheet_title = filename[:-4]  # Remove '.txt' from filename to use as sheet name
        ws = wb.create_sheet(title=sheet_title)

        # Write the DataFrame to the worksheet
        for r in dataframe_to_rows(filtered_data, index=False, header=True):
            ws.append(r)

        # Load the plot image
        plot_buffer.seek(0)  # Rewind the buffer
        image = Image(plot_buffer)
        # Insert the image into the worksheet
        ws.add_image(image, 'E1')  # Place the image starting from cell E1

# Save the workbook to the specified directory
wb.save(os.path.join(directory, 'benzhydrylpyridinium_ions_Q1.xlsx'))

