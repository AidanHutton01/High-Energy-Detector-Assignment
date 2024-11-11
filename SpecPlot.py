'''This script takes gamma ray detector data and plots the spectrum
Inputs - detector data file (must be .mca or .Spe)
        - *optional* name of source/measurment to be added to the title
Outputs - plot of data showing the spectrum (counts/channels)
'''
#import packages
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#define arguments for the script
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", type=str, help="Enter the name or directory of the data file")
    parser.add_argument("-s", "--source", type=str, help="Enter the name of the soure to be plotted", default='Some Source')
    return parser.parse_args()

#function to read the file and generate the count and channel data
def read_file(fname):
#I prefer to read the data with pandas, but that requiers header and footer lengths
#header is always 11 for every file but footer changes

#file is opened to check footer length
    lines = open(fname, 'r').readlines()
    lines = [line.strip() for line in lines]
    for i, line in enumerate(lines):
        #if statment finds start of footer
        if line.startswith('$ROI:') or line.startswith('<<END>>'):
            foot = len(lines)-i
            
#file is being read twice which is a bit inefficent, but if I only used open to read it would take more lines to extract the data
    data = pd.read_csv(fname, header=11, skipfooter=foot , names=['counts'], encoding= "ISO-8859-1", engine='python')
#set the number of channels (first channel is 0 to match indexing)
    channels = np.arange(0,data.size,1)
    return data, channels

#function to plot the spectrum, uses the source name for the title
def plot_data(x,y,title):
    plt.plot(x,y)
    plt.xlabel('Channels Number')
    plt.ylabel('Counts')
    plt.title(f'Spectrum of {title}')
    plt.show()

#main function for the script
def main(fname, source):        
    data, channels = read_file(fname)
    return plot_data(channels, data['counts'], source)
    
#script parses arguments then uses the file name arg to run main

if __name__ == '__main__':
    args = arg_parser()
    main(args.fname, args.source)