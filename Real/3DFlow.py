#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  9 10:38:00 2018
    Plot mean flow or a slice of a 3D flow
@author: Weibo Hu
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from DataPost import DataPost 
from scipy.interpolate import interp1d
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from scipy.interpolate import griddata
from scipy.interpolate import spline
import scipy.optimize
from numpy import NaN, Inf, arange, isscalar, asarray, array
import time
import sys

plt.close ("All")
plt.rc('text', usetex=True)
font1 = {'family' : 'Times New Roman',
         'color' : 'k',
         'weight' : 'normal',
         'size' : 12,}

font2 = {'family' : 'Times New Roman',
         'color' : 'k',
         'weight' : 'normal',
         'size' : 14,
        }

font3 = {'family' : 'Times New Roman',
         'color' : 'k',
         'weight' : 'normal',
         'size' : 16,
}

path = "/media/weibo/Data1/BFS_M1.7L_fine/DataPost/"
path1 = "/media/weibo/Data1/BFS_M1.7L_fine/probes/"
path2 = "/media/weibo/Data1/BFS_M1.7L_fine/DataPost/"
#path3 = "D:/ownCloud/0509/Data/"
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'

#%% Import Data
MeanFlow = DataPost()
VarName  = ['x', 'y', 'z', 'u', 'v', 'w', \
            'rho', 'p', 'Q_crit', 'Mach', 'a', 'T']
#MeanFlow.UserData(VarName, path+'t307.txt', 1, Sep = '\t')
#MeanFlow.SpanAve(path+'MeanSlice307.dat')
MeanFlow.LoadData(path+'MeanSlice307.dat', Sep = '\t')
x, y = np.meshgrid(np.unique(MeanFlow.x), np.unique(MeanFlow.y))
rho  = griddata((MeanFlow.x, MeanFlow.y), MeanFlow.rho, (x, y))
#%% Plot contour of the mean flow field
corner = (x<0.0) & (y<0.0)
rho[corner] = np.nan
fig, ax = plt.subplots(figsize=(10, 3))
rg1 = np.linspace(0.25, 1.06, 13)
cbar = ax.contourf(x, y, rho, cmap = 'rainbow', levels = rg1)
ax.set_xlim(np.min(x), np.max(x))
ax.set_ylim(np.min(y), np.max(y))
ax.set_xlabel(r'$x/\delta_0$', fontdict = font2)
ax.set_ylabel(r'$y/\delta_0$', fontdict = font2)
ax.grid (b=True, which = 'both', linestyle = ':')
plt.gca().set_aspect('equal', adjustable='box')
# Add colorbar
rg2 = np.linspace(0.25, 1.06, 4)
cbaxes = fig.add_axes([0.68, 0.65, 0.2, 0.07]) # x, y, width, height
cbar = plt.colorbar(cbar, cax = cbaxes, orientation="horizontal", ticks=rg2)
cbaxes.set_ylabel(r'$\rho/\rho_{\infty}$', \
                  fontdict = font2, rotation = 0, labelpad = 20)
# Add iosline for Mach number
ax.tricontour(MeanFlow.x, MeanFlow.y, MeanFlow.Mach, \
              levels = 1.0, linewidths=1.0, colors='k')
# Add isoline for boudary layer edge
u  = griddata((MeanFlow.x, MeanFlow.y), MeanFlow.u, (x, y))
umax = u[-1,:]
#umax = np.amax(u, axis = 0)
rg2  = (x[1,:]<40.0) # in front of the shock wave 
umax[rg2] = 1.0
u  = u/(np.transpose(umax))
u[corner] = np.nan # mask the corner
rg1 = (y>0.3*np.max(y)) # remove the upper part
u[rg1]     = np.nan
ax.contour(x, y, u, levels = 0.99, linewidths = 1.0, colors='w')
#plt.tight_layout(pad = 0.5, w_pad = 0.2, h_pad = 0.2)
plt.savefig(path+'Test.svg', bbox_inches='tight')
plt.show()