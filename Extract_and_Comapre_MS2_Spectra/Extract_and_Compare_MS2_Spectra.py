import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import find_peaks

# Dictionary of compounds and their parent masses
parent_masses = {
    "Acetylfentanyl": 323.2,
    "Alfentanyl": 417.2,
    "Carfentanyl": 395.2,
    "Fentanyl": 337.2,
    "Sufentanyl": 387.2,
    "4-ANPP": 281.2
}

def find_parent_peak_area(intensity, mass, parent_mass):
    # Find peaks in the spectrum
    peaks, _ = find_peaks(intensity, height=0)
    # Find the peak closest to the parent mass
    parent_peak = peaks[np.argmin(np.abs(mass[peaks] - parent_mass))]
    # Assuming the peak area is represented by the peak intensity for simplicity
    # For a more accurate estimation, integrate the area around the peak
    parent_peak_area = intensity[parent_peak]
    return parent_peak_area

def interpolate_and_normalize(file_path, parent_mass):
    # Read data
    data = pd.read_csv(file_path, sep='\t')
    mass, intensity = data['Mass/Charge'].values, data['Intensity'].values

    # Interpolate
    f = interp1d(mass, intensity, kind='linear', fill_value="extrapolate")
    new_mass = np.arange(50, 450.1, 0.1)
    new_intensity = f(new_mass)

    # Find parent peak area
    parent_peak_area = find_parent_peak_area(new_intensity, new_mass, parent_mass)
    return new_mass, new_intensity, parent_peak_area

def process_directory(directory):
    # Create a DataFrame to store final results
    final_df = pd.DataFrame()
    final_df['Mass/Charge'] = np.arange(50, 450.1, 0.1)

    # Group files by the first entry in their filename
    file_groups = {}
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            compound_name = file.split('_')[0]
            if compound_name in file_groups:
                file_groups[compound_name].append(file)
            else:
                file_groups[compound_name] = [file]

    # Process each group of files
    for compound, files in file_groups.items():
        parent_mass = parent_masses.get(compound)
        if parent_mass is None:
            print(f"Parent mass for {compound} not found. Skipping.")
            continue

        # Store data and parent peak areas
        spectra_data = {}
        for file in files:
            file_path = os.path.join(directory, file)
            mass, intensity, parent_peak_area = interpolate_and_normalize(file_path, parent_mass)
            spectra_data[file] = (mass, intensity, parent_peak_area)

        # Find the maximum parent peak area in the group
        max_parent_peak_area = max([data[2] for data in spectra_data.values()])

        # Normalize based on parent peak 
        for file, (mass, intensity, parent_peak_area) in spectra_data.items():
            normalized_intensity = intensity * (max_parent_peak_area / parent_peak_area)
            #normalized_intensity /= np.max(normalized_intensity)
            final_df[file] = normalized_intensity

    # Save to Excel
    final_df.to_excel(os.path.join(directory, 'normalized_mass_spectra.xlsx'), index=False)

# Use the function
process_directory(r'G:\Hopkins_Laboratory\Fentanyl_Analogs\DMS_Data\Extracted_Data\MS2_N2')
