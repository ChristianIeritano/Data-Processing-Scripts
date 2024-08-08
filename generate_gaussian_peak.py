'''
Author: CI
2024-08-07
A code to generate gaussian functions with user defined peak heights and fwhm. Utility is for overlaying calculated CCSs with drift tube data
'''

import numpy as np
import csv, os

def gaussian(x, height, sigma, centroid):
    '''Generate Gaussian function values.'''
    return height * np.exp(-((x - centroid) ** 2) / (2 * sigma ** 2))

def generate_gaussian_data(height, sigma, centroid, x_start, x_end, x_step):
    '''Generate Gaussian data for given parameters.'''
    x_values = np.arange(x_start, x_end, x_step)
    y_values = gaussian(x_values, height, sigma, centroid)
    return x_values, y_values

def write_to_csv(filename, x_values, y_values):
    '''Write x, y data to a CSV file.'''
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y'])
        writer.writerows(zip(x_values, y_values))

def main():
    #Gaussian peak params
    height = 0.4 #height of gaussian
    sigma = 2.8 # fwhm of gaussian
    centroid = 173.3
    
    #Range of data to plat and export
    x_start = 160
    x_end = 200
    x_step = 0.2
    
    #Directory and filename
    directory = r'C:\Users\Chris\OneDrive - University of Waterloo\Waterloo\Projects\2024\Ciprofloxacin\Mobility_Sims'
    filename = f'Expt_Oprot_{str(centroid)}.csv'

    # Output file path
    outfile = os.path.join(directory, filename)

    # Generate Gaussian data
    x_values, y_values = generate_gaussian_data(height, sigma, centroid, x_start, x_end, x_step)

    # Write data to CSV
    write_to_csv(outfile, x_values, y_values)

    print(f'Data written to {filename}')

if __name__ == '__main__':
    main()
