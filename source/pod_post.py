#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 11:00:39 2018
    This code for POD post processing.
@author: weibo
"""
#%% Load necessary module
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pod as pod
import plt2pandas as p2p
import variable_analysis as va
from timer import timer
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from scipy.interpolate import griddata
import os
import sys

plt.close("All")
plt.rc('text', usetex=True)
font = {
    'family': 'Times New Roman',  # 'color' : 'k',
    'weight': 'normal',
}

class OOMFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
        self.oom = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(
                self,useOffset=offset,useMathText=mathText)
    def _set_orderOfMagnitude(self, nothing):
        self.orderOfMagnitude = self.oom
    def _set_format(self, vmin, vmax):
        self.format = self.fformat
        if self._useMathText:
            self.format = '$%s$' % matplotlib.ticker._mathdefault(self.format)

plt.close("All")
plt.rc('text', usetex=True)
font = {
    'family': 'Times New Roman',  # 'color' : 'k',
    'weight': 'normal',
}

matplotlib.rcParams["xtick.direction"] = "in"
matplotlib.rcParams["ytick.direction"] = "in"
textsize = 13
numsize = 10

# %%############################################################################
"""
    Load data
"""
# %% load data
path = "/media/weibo/VID2/BFS_M1.7TS_LA/"
p2p.create_folder(path)
pathP = path + "probes/"
pathF = path + "Figures/"
pathM = path + "MeanFlow/"
pathS = path + "SpanAve/"
pathT = path + "TimeAve/"
pathI = path + "Instant/"
pathD = path + "Domain/"
pathPOD = path + "POD/"
pathSS = path + 'Slice/TP_2D_S_10/'
timepoints = np.arange(700, 999.5 + 0.5, 0.5)
dirs = sorted(os.listdir(pathSS))
if np.size(dirs) != np.size(timepoints):
    sys.exit("The NO of snapshots are not equal to the NO of timespoints!!!")
DataFrame = pd.read_hdf(pathSS + dirs[0])
DataFrame['walldist'] = DataFrame['y']
DataFrame.loc[DataFrame['x'] >= 0.0, 'walldist'] += 3.0
grouped = DataFrame.groupby(['x', 'y'])
DataFrame = grouped.mean().reset_index()
NewFrame = DataFrame.query("x>=-5.0 & x<=30.0 & walldist>=0.0 & y<=5.0")
#NewFrame = DataFrame.query("x>=9.0 & x<=13.0 & y>=-3.0 & y<=5.0")
ind = NewFrame.index.values
xval = DataFrame['x'][ind] # NewFrame['x']
yval = DataFrame['y'][ind] # NewFrame['y']
x, y = np.meshgrid(np.unique(xval), np.unique(yval))
x1 = -5.0
x2 = 25.0
y1 = -3.0
y2 = 5.0
#with timer("Load Data"):
#    Snapshots = np.vstack(
#        [pd.read_hdf(InFolder + dirs[i])['u'] for i in range(np.size(dirs))])
var0 = 'u'
var1 = 'v'
var2 = 'p'
col = [var0, var1, var2]
fa = 1 #/(1.7*1.7*1.4)
FirstFrame = DataFrame[col].values
Snapshots = FirstFrame[ind].ravel(order='F')

# %%
with timer("Load Data"):
    for i in range(np.size(dirs)-1):
        TempFrame = pd.read_hdf(pathSS + dirs[i+1])
        grouped = TempFrame.groupby(['x', 'y'])
        TempFrame = grouped.mean().reset_index()
        if np.shape(TempFrame)[0] != np.shape(DataFrame)[0]:
            sys.exit('The input snapshots does not match!!!')
        NextFrame = TempFrame[col].values
        Snapshots = np.vstack((Snapshots, NextFrame[ind].ravel(order='F')))
        DataFrame += TempFrame
Snapshots = Snapshots.T
# Snapshots = Snapshots[ind, :]
# Snapshots = Snapshots*fa
m, n = np.shape(Snapshots)
o = np.size(col)
if (m % o != 0):
    sys.exit("Dimensions of snapshots are wrong!!!")
m = int(m/o)
AveFlow = DataFrame/np.size(dirs)
meanflow = AveFlow.query("x>=-5.0 & x<=30.0 & y>=-3.0 & y<=5.0")

# %%############################################################################
"""
    Compute
"""
# %% POD
varset = { var0: [0, m],
           var1: [m, 2*m],
           var2: [2*m, 3*m]
        }
if np.size(dirs) != np.size(timepoints):
    sys.exit("The NO of snapshots are not equal to the NO of timespoints!!!")

with timer("POD computing"):
    eigval, eigvec, phi, coeff = \
        pod.pod(Snapshots, fluc=True, method='svd')

meanflow.to_hdf(pathPOD + 'Meanflow.h5', 'w', format='fixed')
np.save(pathPOD + 'eigval', eigval)
np.save(pathPOD + 'eigvec', eigvec)
np.save(pathPOD + 'phi1', phi[:, :300])
np.save(pathPOD + 'phi2', phi[:, 300:])
np.save(pathPOD + 'coeff', coeff)

# Eigvalue Spectrum
EFrac, ECumu, N_modes = pod.pod_eigspectrum(80, eigval)
np.savetxt(path+'EnergyFraction600.dat', EFrac, fmt='%1.7e', delimiter='\t')

# %%############################################################################
"""
    Plot
"""
var = var0
matplotlib.rc('font', size=textsize)
fig1, ax1 = plt.subplots(figsize=(3.2,3.0))
xaxis = np.arange(0, N_modes + 1)
ax1.scatter(
    xaxis[1:],
    EFrac[:N_modes],
    c='black',
    marker='o',
    s=10.0,
)   # fraction energy of every eigval mode
# ax1.legend('E_i')
ax1.set_ylim(bottom=0)
ax1.set_xlabel('Mode', fontsize=textsize)
ax1.set_ylabel(r'$E_i$', fontsize=textsize)
ax1.grid(b=True, which='both', linestyle=':')
ax1.tick_params(labelsize=numsize)
ax2 = ax1.twinx()   # cumulation energy of first several modes
# ax2.fill_between(xaxis, ECumu[:N_modes], color='grey', alpha=0.5)
ESum = np.zeros(N_modes+1)
ESum[1:] = ECumu[:N_modes]
ax2.plot(xaxis, ESum, color='grey', label=r'$ES_i$')
ax2.set_ylim([0, 100])
ax2.set_ylabel(r'$ES_i$', fontsize=textsize)
ax2.tick_params(labelsize=numsize)
plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=1)
plt.savefig(pathPOD+str(N_modes)+'_PODEigSpectrum80.svg', bbox_inches='tight')
plt.show()


# %% specific mode in space
ind = 1
var = var2
fa = 1.7*1.7*1.4 # 1.0  #     
x, y = np.meshgrid(np.unique(xval), np.unique(yval))
newflow = phi[:, ind - 1]*coeff[ind - 1, 0]
modeflow = newflow[varset[var][0]:varset[var][1]]
print("The limit value: ", np.min(modeflow)*fa, np.max(modeflow)*fa)
u = griddata((xval, yval), modeflow, (x, y))*fa
corner = (x < 0.0) & (y < 0.0)
u[corner] = np.nan
matplotlib.rc('font', size=textsize)
fig, ax = plt.subplots(figsize=(3.8, 1.6))
c1 = -0.0025 # -0.01 # -0.006
c2 = -c1 #0.063

lev1 = np.linspace(c1, c2, 11)
lev2 = np.linspace(c1, c2, 6)
cbar = ax.contourf(x, y, u, cmap='RdBu_r', levels=lev1, extend='both')
#ax.contour(x, y, u, levels=lev2, colors='k', linewidths=0.8, extend='both')
#                   colors=('#66ccff', '#e6e6e6', '#ff4d4d'), extend='both')
ax.set_xlim(x1, x2)
ax.set_ylim(y1, y2)
ax.tick_params(labelsize=numsize)
cbar.cmap.set_under('#053061')
cbar.cmap.set_over('#67001f')
ax.set_xlabel(r'$x/\delta_0$', fontsize=textsize)
ax.set_ylabel(r'$y/\delta_0$', fontsize=textsize)
# add colorbar
rg2 = np.linspace(c1, c2, 3)
cbaxes = fig.add_axes([0.25, 0.76, 0.30, 0.07])  # x, y, width, height
cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal",
                     ticks=rg2, extendrect='False')
cbar1.formatter.set_powerlimits((-2, 2))
cbar1.ax.xaxis.offsetText.set_fontsize(numsize)
cbar1.update_ticks()
cbar1.set_label(r'$\varphi_{}$'.format(var), rotation=0,
                x=-0.18, labelpad=-20, fontsize=textsize)
cbaxes.tick_params(labelsize=numsize)
# Add shock wave
shock = np.loadtxt(pathM+'ShockLineFit.dat', skiprows=1)
ax.plot(shock[:, 0], shock[:, 1], 'g', linewidth=1.0)
# Add sonic line
sonic = np.loadtxt(pathM+'SonicLine.dat', skiprows=1)
ax.plot(sonic[:, 0], sonic[:, 1], 'g--', linewidth=1.0)
# Add boundary layer
boundary = np.loadtxt(pathM+'BoundaryEdge.dat', skiprows=1)
ax.plot(boundary[:, 0], boundary[:, 1], 'k', linewidth=1.0)
# Add dividing line(separation line)
dividing = np.loadtxt(pathM+'BubbleLine.dat', skiprows=1)
ax.plot(dividing[:, 0], dividing[:, 1], 'k--', linewidth=1.0)

plt.savefig(pathPOD+var+'_PODMode'+str(ind)+'.svg', bbox_inches='tight')
plt.show()

# %% First several modes with time and WPSD
fig, ax = plt.subplots(figsize=(5, 3))
matplotlib.rc('font', size=textsize)
matplotlib.rcParams['xtick.direction'] = 'in'
matplotlib.rcParams['ytick.direction'] = 'in'
lab = []
NO = [9, 10]
ax.plot(timepoints, coeff[NO[0]-1, :], 'k-', linewidth=1.0)
lab.append('Mode '+str(NO[0]))
ax.plot(timepoints, coeff[NO[1]-1, :], 'k:')
lab.append('Mode '+str(NO[1]))
ax.legend(lab, ncol=2, loc='upper right', fontsize=14,
          bbox_to_anchor=(1., 1.12), borderaxespad=0., frameon=False)
ax.set_xlabel(r'$tu_\infty/\delta_0$', fontsize=textsize)
ax.set_ylabel(r'$a_{}$'.format(var), fontsize=textsize)
ax.tick_params(labelsize=numsize)
plt.grid(b=True, which='both', linestyle=':')
plt.savefig(path+var+'_PODModeTemp' + str(NO[0]) + '.svg', bbox_inches='tight')
plt.show()

fig, ax = plt.subplots(figsize=(5, 4))
matplotlib.rc('font', size=numsize)
freq, psd = va.FW_PSD(coeff[NO[0]-1, :], timepoints, 2.0, opt=1)
ax.semilogx(freq, psd, 'k-', linewidth=1.0)
freq, psd = va.FW_PSD(coeff[NO[1]-1, :], timepoints, 2, opt=1)
ax.semilogx(freq, psd, 'k:')
ax.legend(lab, fontsize=15, frameon=False)
ax.yaxis.offsetText.set_fontsize(numsize)
plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
ax.set_xlabel(r'$f\delta_0/U_\infty$', fontsize=textsize)
ax.set_ylabel('WPSD, unitless', fontsize=textsize)
ax.tick_params(labelsize=numsize)
plt.grid(b=True, which='both', linestyle=':')
plt.savefig(path+var+'_POD_WPSDModeTemp' + str(NO[0]) + '.svg', bbox_inches='tight')
plt.show()
# %% Reconstruct flow field using POD
tind = 0
meanflow = np.mean(Snapshots, axis=1)
x, y = np.meshgrid(np.unique(xval), np.unique(yval))
newflow = phi[:, :N_modes] @ coeff[:N_modes, tind]
modeflow = newflow[varset[var][0]:varset[var][1]]
# np.reshape(phi[:, ind-1], (m,1))@np.reshape(coeff[ind-1, :], (1, n))
u = griddata((xval, yval), meanflow+modeflow, (x, y))
corner = (x < 0.0) & (y < 0.0)
u[corner] = np.nan
matplotlib.rc('font', size=textsize)
fig, ax = plt.subplots(figsize=(10, 4))
matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'
lev1 = np.linspace(-0.20, 1.15, 18)
cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1, extend="both")
ax.set_xlim(x1, x2)
ax.set_ylim(y1, y2)
ax.tick_params(labelsize=numsize)
cbar.cmap.set_under('b')
cbar.cmap.set_over('r')
ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
# add colorbar
rg2 = np.linspace(-0.20, 1.15, 4)
cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
cbaxes.tick_params(labelsize=numsize)
plt.savefig(path+var+'_PODReconstructFlow.svg', bbox_inches='tight')
plt.show()

reconstruct = phi @ coeff
err = Snapshots - (reconstruct + np.tile(meanflow.reshape(m, 1), (1, n)))
print("Errors of POD: ", np.linalg.norm(err)/n)
# %% Test POD using meaning flow
def PODMeanflow(Snapshots):

    with timer("POD mean flow computing"):
        eigval, eigvec, phi, coeff = \
            pod.POD(Snapshots, SaveFolder, method='svd')
    ind = 1
    m, n = np.shape(Snapshots)
    x, y = np.meshgrid(np.unique(xval), np.unique(yval))
    newflow = \
        np.reshape(phi[:, ind-1], (m,1))@np.reshape(coeff[ind-1, :], (1, n))
    meanflow = np.mean(newflow.real, axis=1)
    u = griddata((xval, yval), meanflow, (x, y))
    corner = (x < 0.0) & (y < 0.0)
    u[corner] = np.nan
    matplotlib.rc('font', size=18)
    fig, ax = plt.subplots(figsize=(12, 4))
    lev1 = np.linspace(-0.20, 1.15, 18)
    cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1) #, extend="both")
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    ax.tick_params(labelsize=14)
    cbar.cmap.set_under('b')
    cbar.cmap.set_over('r')
    ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
    ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
    # add colorbar
    rg2 = np.linspace(-0.20, 1.15, 4)
    cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
    cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
    cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
    cbaxes.tick_params(labelsize=14)
    plt.savefig(path+'PODMeanFlow.svg', bbox_inches='tight')
    plt.show()
    # %% Eigvalue Spectrum
    EFrac, ECumu, N_modes = pod.POD_EigSpectrum(95, eigval)
    matplotlib.rc('font', size=14)
    fig1, ax1 = plt.subplots(figsize=(6,5))
    xaxis = np.arange(0, N_modes + 1)
    ax1.scatter(
        xaxis[1:],
        EFrac[:N_modes],
        c='black',
        marker='o',
        s=EFrac[:N_modes]*2,
    )   # fraction energy of every eigval mode
    #ax1.legend('E_i')
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel('Mode')
    ax1.set_ylabel(r'$E_i$')
    ax1.grid(b=True, which='both', linestyle=':')

    ax2 = ax1.twinx()   # cumulation energy of first several modes
    #ax2.fill_between(xaxis, ECumu[:N_modes], color='grey', alpha=0.5)
    ESum = np.zeros(N_modes+1)
    ESum[1:] = ECumu[:N_modes]
    ax2.plot(xaxis, ESum, color='grey', label=r'$ES_i$')
    ax2.set_ylim([0, 100])
    ax2.set_ylabel(r'$ES_i$')
    fig1.set_size_inches(5, 4, forward=True)
    plt.tight_layout(pad=0.5, w_pad=0.2, h_pad=1)
    plt.savefig(path+'MeanPODEigSpectrum.svg', bbox_inches='tight')
    plt.show()
    #%% Original MeanFlow
    origflow = np.mean(Snapshots, axis=1)
    u = griddata((xval, yval), origflow, (x, y))
    corner = (x < 0.0) & (y < 0.0)
    u[corner] = np.nan
    matplotlib.rc('font', size=18)
    fig, ax = plt.subplots(figsize=(12, 4))
    lev1 = np.linspace(-0.20, 1.15, 18)
    cbar = ax.contourf(x, y, u, cmap='rainbow', levels=lev1) #, extend="both")
    ax.set_xlim(x1, x2)
    ax.set_ylim(y1, y2)
    ax.tick_params(labelsize=14)
    cbar.cmap.set_under('b')
    cbar.cmap.set_over('r')
    ax.set_xlabel(r'$x/\delta_0$', fontdict=font)
    ax.set_ylabel(r'$y/\delta_0$', fontdict=font)
    # add colorbar
    rg2 = np.linspace(-0.20, 1.15, 4)
    cbaxes = fig.add_axes([0.16, 0.76, 0.18, 0.07])  # x, y, width, height
    cbar1 = plt.colorbar(cbar, cax=cbaxes, orientation="horizontal", ticks=rg2)
    cbar1.set_label(r'$u/u_{\infty}$', rotation=0, fontdict=font)
    cbaxes.tick_params(labelsize=14)
    plt.savefig(path+'OrigMeanFlow.svg', bbox_inches='tight')
    plt.show()
    print("Errors of MeanFlow: ", np.linalg.norm(meanflow - origflow)/n)
#%% POD for mean flow
# PODMeanflow(Snapshots)
