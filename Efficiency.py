'''Script for
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import Calibrate
import Resolution
import pandas as pd
import argparse

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=str, help="Enter the name or directory of the outputted data file from Calibrate.py")
    return parser.parse_args()

#function uses gauss fit from calibration to find counts per second of each peak
def get_cps(fname):
    #reads data from Calibrate.py as in Resolution.py
    peak_data, detec_data = Resolution.read_data(fname)
    #double peaks are harder to evaluate so a truth array is made to remove them
    w = [not i.endswith('D') for i in peak_data['Peak']]

    tot_counts = []
    energies = []
    for i in peak_data[w]['Peak']:
        energies.append(float(i.split()[1]))

    x = []
    for u,l in zip(peak_data[w]['U_lim'],peak_data[w]['L_lim']):
        x.append(np.arange(l,u+1,1))
    for i,mu,sig,Am,a,b,c in zip(x,peak_data[w]['Mean'],peak_data[w]['Std'],peak_data[w]['Amp'],peak_data[w]['a'],peak_data[w]['b'],peak_data[w]['c']):
        y = Calibrate.gauss_poly_model(i,mu,sig,Am,a,b,c)
        tot_counts.append(sum(y))
    tot_counts
    tot_cps = tot_counts/peak_data['Time'][w]
    return tot_cps, energies, detec_data

#function finds absolute and intrinsic efficiencies
def get_efficiency(cps, G, activity):
    abs_efficiency = cps/activity
    int_efficiency = abs_efficiency/G
    return abs_efficiency, int_efficiency

#Function plots both efficiencies as a function of energy
def plot_efficency(energies, abs_eff, int_eff, channels, title):
    plt.figure(figsize=[12,8])
    plt.subplot(2,1,1)
    plt.scatter(energies,abs_eff)
    plt.title(f'Absolute Efficiency of {title}')
    plt.ylabel('Efficiency')
    plt.subplot(2,1,2)
    plt.scatter(energies,np.log(int_eff))
    plt.title(f'Intrinsic Efficiency of {title}')
    plt.xlabel('Energy (keV)')
    plt.ylabel('Efficiency')
    plt.show()

#main function
def main(fname):
    cps, energies, detec = get_cps(fname)
    if detec['Detector'][0] == 'BGO':
        activity = [409891, 160352, 18946, 1032, 1032]
        A = np.pi*(2.54**2)
    if detec['Detector'][0] == 'NaI':
        activity = [409891, 160352, 18946]
        A = np.pi*(2.84**2)
    if detec['Detector'][0] == 'CdTe':
        activity = [409891, 409891, 18946]
        A = 0.25
    G = A/(4*np.pi*(15**2))
    
    abs_eff, int_eff = get_efficiency(cps, G, activity)
    plot_efficency(energies,abs_eff,int_eff,detec['Channels'][0], detec['Detector'][0])
    
if __name__ == '__main__':
    args = arg_parser()
    main(args.data)