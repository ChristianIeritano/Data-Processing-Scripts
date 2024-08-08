import pyopenms as oms
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import os

def process_mzml_LC_MRM(mzml_file):
    exp = oms.MSExperiment()
    oms.MzMLFile().load(mzml_file, exp)
    
    #dict to store MRM data
    mrm_data = {}

    #if I understand the data structure, each MRM channel is a full LC chromatogram
    #this "should" loop through each MRM channel and get the time/int data
    for chromatogram in exp.getChromatograms():
        time_intensity_pairs = chromatogram.get_peaks()
        native_id = chromatogram.getNativeID() #this should be the name you assign to each MRM channel - double check that it wokrs like it think it should
        mrm_data[native_id] = time_intensity_pairs

    #I suspect the time steps sampled for each MRM channel are going to be offset the time of the scan, so well do some interpolation 
    #First, we need the min and max time across all channels to get the interpolation range
    all_times = [time for _, pairs in mrm_data.items() for time, _ in pairs] #real in all times and append to list
    min_time, max_time = min(all_times), max(all_times) #get the min and max
    uniform_time_axis = np.linspace(min_time, max_time, num=100) #apply a linear spacing to the list - adjust the number of points as needed - I set 100

    #dict to store interpoalted data
    interpolated_data = {}
    for native_id, pairs in mrm_data.items():
        time, intensity = zip(*pairs) 
        interp_func = interp1d(time, intensity, bounds_error=False, fill_value='extrapolate') #the function that does the interpolation - this is how scipy interpolation works
        interpolated_data[native_id] = interp_func(uniform_time_axis) #now we do the interpolation 

    #write the interpolated data to a dataframe so we can port that to an excel sheet
    df = pd.DataFrame(interpolated_data, index=uniform_time_axis)
    df.index.name = 'Time'

    return df

def process_directory(directory_path, output_excel_file):
    
    #get list of all mzml files in a directory
    mzml_files = [file for file in os.listdir(directory) if file.lower().endswith('.mzml')]

    with pd.ExcelWriter(output_excel_file) as writer:
        for mzml_file in mzml_files:
            print(f'Processing {mzml_file}...')
            
            #proscess the mzml file
            mrm_df = process_mzml_LC_MRM(mzml_file)
            
            #Use the file name without the extension as the sheet name, anbd write the content of each mzml file to its own sheet in the excel document
            sheet_name = os.path.splitext(os.path.basename(mzml_file))[0][:31]  #Excel sheet names are limited to 31 characters
            mrm_df.to_excel(writer, sheet_name=sheet_name)
            print(f'Data from {mzml_file} written to sheet {sheet_name}')

if __name__ == '__main__':
    directory = r'path_to_your_mzml_files_directory' #directory w/ mzml files (keep it as a raw string, so r'' instead of '')
    output_filename = 'data.xlsx' #must end in .xlsx

    #Process all mzML files in the directory
    process_directory(directory, os.path.join(directory, output_filename))
