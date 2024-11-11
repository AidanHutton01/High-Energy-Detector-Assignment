'''Script for plotting absolute efficiency as a function of angle
'''
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import Calibrate
import Resolution
import Efficiency
import pandas as pd
import argparse

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=str, help="Enter the name or directory of the outputted data file from Calibrate.py")
    return parser.parse_args()

def plot_eff_angle(angles, efficiency, title):
    plt.plot(angles,efficiency)
    plt.title(f'{title}: Absolute Efficency of Americium-241 59.54keV Peak as a Function of Angle')
    plt.xlabel('Angle (degrees)')
    plt.ylabel('Efficiency')
    plt.show()

def main(fname):
    tot_cps, energies, detec_data = Efficiency.get_cps(fname)
    #this is hard coded for Americiuim at these specific angles, not ideal
    activity = 409891
    abs_efficiency = tot_cps/activity
    angles = [0,15,30,45,60,75,90]
    plot_eff_angle(angles, abs_efficiency, detec_data['Detector'][0])
    
if __name__ == '__main__':
    args = arg_parser()
    main(args.data)