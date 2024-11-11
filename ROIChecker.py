'''This script is just for personal use. I'm using it to find the ROI of my data with background removed
'''
#import packages
import argparse
import pandas as pd
import matplotlib.pyplot as plt

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
    return data

#function to plot the spectrum, uses the source name for the title
def plot_data(x,y,title):
    plt.plot(x,y)
    plt.xlabel('Channels Number')
    plt.ylabel('Counts')
    plt.title(f'Spectrum of {title}')
    plt.show()

#main function for the script, checks the file type to set the number of channels (first channel is 0 to match indexing)
def main(fname, source):        
    data = read_file(fname)
    background = read_file('BGO\Background_0degrees_600s_BGO_uncal.Spe')
    channels = range(data.size)
    data_corr = []
    for i in range(data.size):
        if data['counts'][i]-background['counts'][i] < 0:
            data_corr.append(0)
        else:
            data_corr.append(data['counts'][i]-background['counts'][i])
        
    return plot_data(channels, data_corr, source)
    
#script parses arguments then uses the file name arg to run main

if __name__ == '__main__':
    args = arg_parser()
    main(args.fname, args.source)