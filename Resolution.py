'''This script takes the data outputted from Calibrate.py and calculates the resolution of each photopeak measured using the mean and standard deviation of their gaussian fits. A log-log plot of resolution^2/energy is made and all relevant parametes are also written into a .txt file.
Inputs - a data file containing curve_fit parameters for every photopeak and some detector parameters, must follow the same format as the output from Calibrate.py
       -  name of the file where the data will be outputted to
Outputs - A log-log plot of Resolution^2 against energy for the detector, showing one data point for each peak and a line of best fit based on an inverse quadratic model
        - A .txt file containing data for each peak: energy, resolution, FWHM, and any errors, as well as the parameters for the resolution^2/energy curve.
'''

#import relevant packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import Calibrate
import pandas as pd
import argparse

#simple argument parser to deal with the two inputs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Enter the name or directory of the outputted data file from Calibrate.py")
    parser.add_argument("output", type=str, help="Enter the name or directory of the file that you want the resolution data to be entered into")
    return parser.parse_args()

#this function reads the data file, because the file is from Calibrate.py the format is consistent, can just use pandas.read_csv
def read_data(fname):
    col_names_p = ['Peak', 'Time', 'L_lim', 'U_lim', 'Mean', 'Mean_err', 'Std', 'Std_err', 'Amp', 'Amp_err', 'a', 'a_err', 'b', 'b_err', 'c', 'c_err']
    col_names_d = ['Detector', 'a', 'a_err', 'b', 'b_err', 'Channels']
    peak_data = pd.read_csv(fname, header=0, skipfooter=3, names=col_names_p, encoding= "ISO-8859-1", engine='python')
    detec_data = pd.read_csv(fname, header=len(peak_data['Peak'])+2, names=col_names_d, encoding= "ISO-8859-1", engine='python')
    
    return peak_data, detec_data

#this model is for resolution squared, the model for resolution was fitting weirdly
def resolution_squared_model(x,a,b,c):
    return (a/(x**2) + b/x + c)

#this function makes the data necessary for the plot + the outputted data
def generate_res_data(peak_data, detec_data):
    #x is the full channel range for the detector, converted to energy using the parameters from the calibration
    x = np.arange(0,detec_data['Channels'][0],1)
    energy_range = Calibrate.linear(x, detec_data['a'][0], detec_data['b'][0])
    #empty list for peak energies
    energies = []
    for p in peak_data['Peak']:
        energies.append(float(p.split()[1]))
    #some standard deviation values ended up negative so take an absolute value and calculate FWHM
    fwhm = 2*np.sqrt(2*np.log(2))*abs(peak_data['Std'])
    #resolution is just a ratio so don't need to convert channels to energy
    resolution = fwhm/peak_data['Mean']
    
    #error is also calculated for FWHM and resolution of each peak
    #error values are striped of their plus_minus and turned to floats
    n = len(peak_data['Peak'])
    std_err = np.zeros(n)
    mean_err = np.zeros(n)
    for i in range(n):
        std_err[i] = float(peak_data['Std_err'][i].strip(' ±'))
        mean_err[i] = float(peak_data['Mean_err'][i].strip(' ±'))
        
    fwhm_err = 2*np.sqrt(2*np.log(2))*abs(std_err)
    resolution_err = np.sqrt((fwhm_err/fwhm)**2 + (mean_err/peak_data['Mean'])**2)
    
    #list made for outputted data, each item in the list is a string for one
    data_out = []
    for i in range(n):
        data_out.append(peak_data['Peak'][i])
        data_out[i] = ', '.join([data_out[i], f'{fwhm[i]:.2f}, \u00B1{fwhm_err[i]:.2f}, {resolution[i]:.2f}, \u00B1{resolution_err[i]:.2f}'])
    
    return energy_range, energies, resolution, data_out

#this function just takes the data from the previous function to generate the resolution^2/energy graph
def res_energy_plot(energy_range, energies, resolution, title):
    #for curve_fit initail guesses of 1,1,1 are suitable for BGO and NaI. CdTe has covariance error seemingly with any initial guesses so returns inf
    popt, pcov = opt.curve_fit(resolution_squared_model, energies, resolution**2, p0=[1,1,1])
    y_model = resolution_squared_model(energy_range,popt[0],popt[1],popt[2])
    plt.scatter(energies,resolution**2);
    plt.xlabel('Energy (keV)');
    plt.ylabel(f'Resolution\u00b2');
    plt.title(f"{title} Resolution as a Function of Energy");
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(energy_range,y_model, c='r');
    plt.show()
    
    #parameters for resolution curve are stored
    res_out = ['<DETECTOR RESOLUTION MODEL>', 'Detector, a, a_err, b, b_err, c, c_err',]
    res_out.append(title)
    for i in range(3):
        res_out[2] = ', '.join([res_out[2], f'{popt[i]:.2f}, \u00B1{np.sqrt(pcov[i,i]):.2f}'])
    return res_out
                            
def write_data(data, fname):
    with open(fname, "w") as f:
        for d in data:
            print(f'{d}',file=f)

#main function to active the entire script
def main(data, output):
    peak_data, detec_data = read_data(data)
    energy_range, energies, resolution, data_out = generate_res_data(peak_data, detec_data)
    #detector name is used for graph title
    title = detec_data['Detector'][0]
    res_out = res_energy_plot(energy_range, energies, resolution, title)
    #peak data from generate_res_data is added to res_out to be written into the output file
    res_out.append('<PEAK RESOLUTION PARAMETERS>')
    res_out.append('Peak, FWHM, FWHM_err, Res, Res_err')
    for i in data_out:
        res_out.append(i)
    write_data(res_out, output)
    
    
if __name__ == '__main__':
    args = arg_parser()
    main(args.input, args.output)