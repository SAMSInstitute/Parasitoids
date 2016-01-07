#! /usr/bin/env python
"""
Plotting suite for ParasitoidModel

Created on Fri May 08 12:12:19 2015

Author: Christopher Strickland
"""

import numpy as np
import ParasitoidModel as PM
import matplotlib.pyplot as plt
import time

# Implementation detail:
# Formation of each p(x,t_i), fft of each one, and ifft will need to be done in
#   parallel when doing Bayesian inference. fft of 8000^2 is 5.6 sec.
#   Want: number of processors = number of days to simulate

#load some emergence data
c_em = PM.emergence_data('data\carnarvonearl')
#load some wind data
wind_data = PM.read_wind_file('data\carnarvonearl')

#SPATIAL DOMAIN:
# Release point will be placed in the center
# Domain will be defined in terms of distance from release and resolution
# FUTURE: assign cells UTM values when plotting
rad_dist = 8000.0 #distance from release point to a side of the domain (meters)
rad_res = 4000 #number of cells from center to side of domain
               #so, each cell is 2 m**2


dom_len = rad_res*2+1 #number of cells along one dimension of domain
dom_ticks = np.linspace(-rad_dist,rad_dist,dom_len) #label the center of each cell
                                                    #center cell is 0
cell_dist = rad_dist/rad_res #dist from one cell to neighbor cell.

#Here, we really want to solve two problems at the same time
# 1. test the functions in ParasitoidModel
# 2. play with them to get some reasonable dummy parameters

#### Test g function for prob. during different wind speeds ####
def plot_g_wind_prob(aw=1.8,bw=6):
    windr_range = np.arange(0,3.1,0.1) #a range of wind speeds
    plt.ion()
    plt.figure()
    #first scalar centers the logistic. Second one stretches it.
    plt.plot(windr_range,PM.g_wind_prob(windr_range,aw,bw))
    plt.xlabel('wind speed')
    plt.ylabel('probability of flight')
    plt.title('g func for prob of flight during given wind speed')

#### Test f function for prob. during different times of the day    
def plot_f_time_prob(a1=7,b1=1.5,a2=19,b2=1.5):
    n = 240 #throw in a lot of increments to see a smooth 24hr plot
    day_time = np.linspace(0,24,n)
    #first scalar centers the logistic. Second one stretches it.
    #first set of two scalars is the first logistic
    plt.ion()
    plt.figure()
    plt.plot(day_time,PM.f_time_prob(n,a1,b1,a2,b2))
    plt.xlabel('time of day (hrs)')
    plt.ylabel('probability density of flight')
    plt.title('f func for prob of flight during time of day')
    
#### Test h function (and therefore g and f) with data ####
def plot_h_flight_prob(day_wind=wind_data[1],lam=1.):
    day_time = np.linspace(0,24,wind_data[1].shape[0])
    plt.ion()
    plt.figure()
    plt.plot(day_time,PM.h_flight_prob(day_wind,lam,1.8,6,7,2,19,2))
    plt.xlabel('time of day (hrs)')
    plt.ylabel('probability density of flight')
    plt.title('h func for prob of flight given wind')
    
#### Test p function, which gives the 2-D probability density####
hparams = (1., 1.8, 6, 7, 2., 19, 2.)
Dparams = (1, 1, 0)

def plot_prob_mass(day=1,wind_data=wind_data,hparams=hparams,\
Dparams=Dparams,mu_r=0.2,rad_dist=rad_dist,rad_res=rad_res):
    pmf = PM.prob_mass(day,wind_data,hparams,Dparams,mu_r,rad_dist,rad_res)
    #plt.pcolormesh is not practical on the full output. consumes 3.5GB of RAM
    #will need to implement resolution sensitive plotting
    
    # for now, just plot the center cells
    res = 150
    cell_dist = rad_dist/rad_res #dist from one cell to neighbor cell.
    xmesh = np.arange(-res*cell_dist-cell_dist/2,res*cell_dist+cell_dist/2 + 
        cell_dist/3,cell_dist)
    # mask the view at negligible probabilities
    center = np.ma.masked_less(
        pmf[rad_res-res:rad_res+res+1,rad_res-res:rad_res+res+1],0.0001)
    # flip result
    center = np.flipud(center)
    plt.ion()
    plt.figure()
    plt.pcolormesh(xmesh,xmesh,np.flipud(center),cmap='viridis')
    plt.axis([xmesh[0],xmesh[-1],xmesh[0],xmesh[-1]])
    plt.xlabel('East-West (meters)')
    plt.ylabel('North-South (meters)')
    plt.title('Parasitoid prob. after one day')
    plt.colorbar()