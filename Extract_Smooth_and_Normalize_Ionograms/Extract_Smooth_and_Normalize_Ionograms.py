import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.ndimage import convolve1d

def weighted_adjacent_averaging(intensity, weights):
    # Ensure the weights sum to 1 for proper normalization
    weights = np.array(weights) / np.sum(weights)
    # Apply the convolution with the custom weights
    smoothed_intensity = convolve1d(intensity, weights, mode='constant', cval=0.0)
    return smoothed_intensity

def interpolate_and_smooth(file_path, grid, smoothing_rounds=1):
    # Read data
    data = pd.read_csv(file_path, sep='\t')
    #print(data)
    cov, intensity = data['COV'].values, data['Intensity'].values

    # Interpolate
    f = interp1d(cov, intensity, kind='linear', bounds_error=False, fill_value=0)
    new_cov = np.arange(grid[0], grid[1] + grid[2], grid[2])
    new_intensity = f(new_cov)

    # Apply Adjacent averaging smooth multiple times
    weights = [1, 2, 1]  # Simple weighted average with current point being 2x weight of its neighbours
    for _ in range(smoothing_rounds):
        new_intensity = weighted_adjacent_averaging(new_intensity, weights)

    # Normalize to maximum value of 1
    normalized_intensity = new_intensity / np.max(new_intensity)

    return new_cov, normalized_intensity

def process_directory(directory, grid=(0, 20, 0.05), smoothing_rounds=3):
    # Create a DataFrame to store final results
    final_df = pd.DataFrame()
    final_df['COV'] = np.arange(grid[0], grid[1] + grid[2], grid[2])

    # Process each .txt file
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            file_path = os.path.join(directory, file)
            cov, normalized_intensity = interpolate_and_smooth(file_path, grid, smoothing_rounds)
            final_df[file] = normalized_intensity

    # Save to Excel
    final_df.to_excel(os.path.join(directory, 'normalized_ionograms.xlsx'), index=False)

if __name__ == '__main__':
    directory = r'G:\Hopkins_Laboratory\Fentanyl_Analogs\DMS_Data\Extracted_Data\Ionograms\N2'
    grid=(0, 20, 0.05)
    smoothing_rounds=3
    process_directory(directory, grid, smoothing_rounds)
