'''This script takes a config file (see Example_config) containing gamma ray detector data and plots a calibration curve for the detector.
Inputs - config file (must follow the same format as Example_config)
       - name of the file where the data will be outputted to
Outputs - a plot of a linear calibration curve showing the energy values of each channel in the detector
        - a .txt file containing all the relevant curvefitted parameters of each region of interest and their uncertainties, as well as
'''
import matplotlib.pyplot as plt
import argparse
import SpecPlot
import scipy.optimize as opt
import numpy as np

#simple argument parser to deal with the two inputs
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=str, help="Enter the name or directory of the config file, check ConfigTemplate.txt for formatting")
    parser.add_argument("output", type=str, help="Enter the name or directory of a text file you want the data to be output into")
    return parser.parse_args()

#guassian combined with a second order polynomial for curve fitting peaks
def gauss_poly_model(x,mu,sig,amp,a,b,c):
    return (amp/(np.sqrt(2*np.pi)*sig))*(np.exp(-((x-mu)**2)/(2*sig**2))) + a*x**2 + b*x + c

#a combined model with two gaussians and a second order polynomial for curve fitting overlapping peaks (as seen in barium)
def gauss_gauss_poly_model(x,mu1,sig1,amp1,mu2,sig2,amp2,a,b,c):
    return (amp1/(np.sqrt(2*np.pi)*sig1))*(np.exp(-((x-mu1)**2)/(2*sig1**2))) + (amp2/(np.sqrt(2*np.pi)*sig2))*(np.exp(-((x-mu2)**2)/(2*sig2**2)))  + a*x**2 + b*x + c

#a linear model for fitting the detector calibration curve
def linear(x,a,b):
    return a*x + b

#this function takes the config file and extracts the relevant data from it, it creates 2 dictionaries one for general data and another for region of interest (ROI) data. It also outputs data for the background measurement. This function is quite long and could have been broken up, but it seemed easier to record all the data at once.
def read_config(fname):
#reads each line of config file an prepares it for sorting
    file = open(fname,'r')
    lines = file.readlines()
    lines = [line.strip() for line in lines]
#data from config is first stored in lists so that a dictionary of varying length can be made    
    names = []
    files = []
    times = []
    for line in lines:
        if line.startswith('DETECTOR'):
            detector = line.split()[1]
        if line.startswith('NAME'):
            names.append(line.split()[1])
        if line.startswith('FILE'):
            files.append(line.split()[1])
            test = line
        if line.startswith('TIME'):
            times.append(line.split()[1])
#background data stored for correction
        if line.startswith('BGFILE'):
            bg_data, null = SpecPlot.read_file(line.split()[1])
        if line.startswith('BGTIME'):
            bg_time = int(line.split()[1])
            
#nested dictionary for basic source data {name: {file dir,time of measurment}}
    dic = {}
    for n, f, t in zip(names, files, times):
        i = names.index(n)
        dic[n]={'File':f, 'Time':int(t)}
        
#ROI data is handeled a bit differently, stored in another nested dictionary:
#{source: {peak energy: {ROI limits, initial guesses for curve_fit}}}
    roi = {}
    
    #nested for loops record every region of interest for every source
    for i in range(len(names)):
        roi[names[i]]={}
        for line in lines:
            #if statement checks if the ROI is a single peak or 2 overlapping peaks
            if line.startswith(f'S{i+1}ROI'):
                j = line.split()
                L = [int(j[2]),int(j[3])]
                g = [int(j[5]),int(j[6]),int(j[7]),1,1,1]
                roi[names[i]][j[1]]={'Limits':L, 'Guess':g}
    #overlapping peaks are labled with 'D_' in the config, the lable for the ROI in the dictionary contains both peaks energy values
            if line.startswith(f'S{i+1}D_ROI'):
                j = line.split()
                L = [int(j[3]),int(j[4])]
                g = [int(j[6]),int(j[7]),int(j[8]),int(j[9]),int(j[10]),int(j[11]),1,1,1]
                roi[names[i]][f'{j[1]} {j[2]}']={'Limits':L, 'Guess':g}
            if line.startswith(f'S{i+2}'):
                break
                
    return dic, roi, bg_data, bg_time, detector

#this function uses all the data from read_config to fit each peak and generates 2 lists of mean channel values and their respective energies. Also returns the full range of channels to be used in plotting and records all optimised values for each curve fit with uncertainties.
def peak_fit(dic, roi, bg_data, bg_time):
    #generate empty lists for data to be stored
    energy = []
    peak_channel = []
    optimal_values = []
    #i iterate is used for accessing each element of optimal_values to store all the data, i increases by 1 after each peak is processed
    i = 0
    #d1 & d2 are indexes for the popt and pcov matrixes of double peak regions, optimal values for both peaks are separted when written in to the output file so that the data length matches the single peaks
    d1 = [0,1,2,6,7,8]
    d2 = [3,4,5,6,7,8]
    for n in roi.keys():
        #count data is read and background removed
        data, channels = SpecPlot.read_file(dic[n]['File'])
        data_corr = data['counts']-bg_data['counts']*(dic[n]['Time']/bg_time)
        #nested for loop goes through every ROI
        for k in roi[n].keys():
            #L - limits of ROI, g - initial gueses for curve_fit
            L, g = roi[n][k]
            #begining and end of ROI
            b, e = roi[n][k][L]
            #if statment checks wether the ROI is 2 overlapping peaks or a normal peak
            #for a double peak ROI, 2 values are added for energy and peak_channel, and 2 lines of curve_fit data are added to optimal_values
            if ' ' in k:
                popt, pcov = opt.curve_fit(gauss_gauss_poly_model, channels[b:e], data_corr[b:e], p0=roi[n][k][g])
                energy.append(float(k.split()[0]))
                energy.append(float(k.split()[1]))
                peak_channel.append(int(popt[0]))
                peak_channel.append(int(popt[3]))
                #when dealing with a double peak, each one has its own row in optimal_values
                optimal_values.append(f"{n} {k.split()[0]} D, {dic[n]['Time']}, {b}, {e}")
                for j in d1:
                    optimal_values[i] = ', '.join([optimal_values[i], f'{popt[j]:.2f}, \u00B1{np.sqrt(pcov[j][j]):.2f}'])
                i+=1    
                optimal_values.append(f"{n} {k.split()[1]} D, {dic[n]['Time']}, {b}, {e}")
                for j in d2:
                    optimal_values[i] = ', '.join([optimal_values[i], f'{popt[j]:.2f}, \u00B1{np.sqrt(pcov[j][j]):.2f}'])
                    
            #single peaks are processed this way        
            else:
                popt, pcov = opt.curve_fit(gauss_poly_model, channels[b:e], data_corr[b:e], p0=roi[n][k][g])
                energy.append(float(k))
                peak_channel.append(int(popt[0]))
                optimal_values.append(f"{n} {k}, {dic[n]['Time']}, {b}, {e}")
                for j in range(len(popt)):
                    optimal_values[i] = ', '.join([optimal_values[i], f'{popt[j]:.2f}, \u00B1{np.sqrt(pcov[j][j]):.2f}'])
            i+=1
                
    return energy, peak_channel, channels, optimal_values

#this function takes the outputs from peak_fit and plots the data points for calibration as well as the linear calibration line
#also outputs curve fit parameters for the calibration
def plot_calibration(energy, peak_channel, channels, title):
    params = title
    popt, pcov = opt.curve_fit(linear, peak_channel, energy, p0=[1,1])
    lin_y = linear(channels, popt[0],popt[1])
    
    for j in range(len(popt)):
        params = ', '.join([params, f'{popt[j]:.2f}, \u00B1{np.sqrt(pcov[j][j]):.2f}'])
    
    plt.figure(figsize=[12,7])
    plt.scatter(peak_channel, energy);
    plt.plot(channels,lin_y, c='r');
    plt.xlabel('Channel Number')
    plt.ylabel('Energy (keV)')
    plt.title(f'{title} Detector Calibration Plot')
    plt.show()
    return params

#function for writing the curve fitting data into a file
def write_data(data, fname):
    with open(fname, "w") as f:
        print('Peak, Time, L_lim, U_lim, Mean, Mean_err, Std, Std_err, Amp, Amp_err, a, a_err, b, b_err, c, c_err', file=f)
        for d in data:
            print(f'{d}',file=f)
        
    
#main function
def main(config, output):
    dic, roi, bg_data, bg_time, detector = read_config(config)
    energy, peak_channel, channels, optimals = peak_fit(dic, roi, bg_data, bg_time)
    cali_params = plot_calibration(energy, peak_channel, channels, detector)
    #adds detector parameters to optimals to be written into the output
    optimals.append('<DETECTOR CALIBRATION VALUES>')
    optimals.append('Detector, a, a_err, b, b_err, Channels')
    optimals.append(cali_params)
    optimals[-1] = ', '.join([optimals[-1], f'{len(channels)}'])
    write_data(optimals, output)
    
if __name__ == '__main__':
    args = arg_parser()
    main(args.config, args.output)