import os
import csv
import numpy as np
from scipy.signal import find_peaks

def parse_line(line, delimiter):
    return line.strip().split(delimiter)

def process_file(filename, do_nothing_list, target_mz_list, scale_peak_factor, scale_background_factor, tolerance, height=None):
    if filename.endswith('.csv'):
        delimiter = ','
    elif filename.endswith('.txt'):
        delimiter = ' '
    else:
        raise ValueError("Unsupported file format. Only .csv and .txt are supported.")

    mz_values = []
    intensity_values = []

    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)
        next(reader) #skip header
        for row in reader:
            if len(row) != 2:
                raise ValueError("Each line must contain exactly 2 columns (m/z and intensity).")
            mz, intensity = map(float, row)
            mz_values.append(mz)
            intensity_values.append(intensity)

    mz_values = np.array(mz_values)
    intensity_values = np.array(intensity_values)

    # Find peaks
    peaks, _ = find_peaks(intensity_values, height=height)

    # Identify which peaks are in the target_mz_list
    target_indices = []
    ignore_indicies = []
    for peak in peaks:
        mz = mz_values[peak]
        if any(abs(mz - target_mz) <= tolerance for target_mz in target_mz_list):
            target_indices.append(peak)
        elif any(abs(mz - target_mz) <= tolerance for target_mz in do_nothing_list):
            ignore_indicies.append(peak)

    # Scaling the intensity values
    scaled_intensity_values = intensity_values.copy()
    for i in range(len(intensity_values)):
        if i in target_indices:
            scaled_intensity_values[i] *= scale_peak_factor
        elif i in ignore_indicies:
            scaled_intensity_values[i] *= 1.
        else:
            scaled_intensity_values[i] *= scale_background_factor

    return mz_values, scaled_intensity_values

def write_to_file(filename, mz_values, intensity_values):
    out_file = f'{os.path.splitext(filename)[0]}_mod.csv'
    with open(out_file, 'w', newline='') as file:
        file.write('mz,intensity_mod\n')
        writer = csv.writer(file)
        for mz, intensity in zip(mz_values, intensity_values):
            writer.writerow([mz, intensity])

if __name__ == "__main__":
    directory = r'C:\Users\Chris\OneDrive - University of Waterloo\Waterloo\Manuscripts\2024\Fentanyl_Prototropic_Isomers\UVPD_extraction\FuranylFentanyl_LowPower\Figures\UVPD_data'
    input_filename = os.path.join(directory, 'UVPD_Furent_Oprot_262nm_CD3OD.csv')  # or 'input.txt'
    do_nothing_list = [376.15] #parent m/z and any other peaks you want to ignore
    #target_mz_list = [280.19,228.15,188.2,170.16]  # list of m/z values to be scaled
    target_mz_list = [281.15,280.19,188.2,189.2,170.16]  # list of m/z values to be scaled
    #target_mz_list = [189.1,188.1]
    scale_peak_factor = 6  # user-defined factor for scaling peaks
    scale_background_factor = 0.2  # user-defined factor for scaling background
    tolerance = 0.2  # tolerance in Da for matching m/z values
    peak_height = None  # Optionally set a minimum height for peaks

    mz_values, scaled_intensity_values = process_file(input_filename, do_nothing_list, target_mz_list, scale_peak_factor, scale_background_factor, tolerance, height=peak_height)
    write_to_file(input_filename, mz_values, scaled_intensity_values)
    print(f"Processed data has been written to the output file.")
