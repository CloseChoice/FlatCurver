import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
#os.getcwd()
os.chdir("/Users/schmidle/Documents/GIT-Projects/FlatCurver/")
#os.chdir("/Users/schmidle/Documents/GIT-Projects/FlatCurver/api/FlatCurver/simulation/PandemicSimulator")
# automatic reloading the packages to keep tehm uodated)
#%load_ext autoreload
#%autoreload 2
module_folder = os.path.abspath('/Users/schmidle/Documents/GIT-Projects/FlatCurver/api')
if module_folder not in sys.path:
    sys.path.append(module_folder)

import FlatCurver.simulation.PandemicSimulator.PandemicSimulatorMulti as pan
import FlatCurver.simulation.PandemicSimulator.PandemicSimulator as pansingle
import FlatCurver.simulation.PandemicSimulator.FitPandemicSimulator as panfit


### Normal Multi
# ger_pop = 8*10e7  #german population
# ndim = 2
# beta = np.array([[1, 3/10], [1/10, 2/10]])  # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
# gamma = np.diag([0.97/14, 0.96/14])  #recovery rate: 0.97 percent survive while the average infection lasts for 14 days
# delta = np.diag([0.03/14, 0.04/14])  #death rate: 1-gamma
# N = np.array([0.6*ger_pop, 0.4 * ger_pop])
# timesteps = 100
# group_names=["a","b"]
# # %% codecell
# multi_pan = pan.PandemicSimulatorMulti(beta=beta, gamma=gamma, delta=delta, N=N, group_names=group_names, timesteps=timesteps)
# # %% codecell
# multi_pan.set_y0([N[0]-1, N[1], 0, 0, 1,0, 0,0])
# # %% codecell
# sol = multi_pan.simulate_SEIR()
# # %% codecell
# multi_pan.simulate_and_show_results()

### MyCalibration (only single input model)
# ger_pop = 8*10e7  #german population
 # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
# N = 8*10e7  #german population
# try if single simulator still works
# pans = pansingle.PandemicSimulator(beta=beta, gamma=gamma, delta=delta, N=N, timesteps=timesteps,group_names=group_names)
# pans.set_y0(y0)
# # pans.simulate_and_show_results()
# df = pans.simulate_extract_df()
# df-dummy_y
# FIT
################
###PREPARE DATA
################

# get data
indata = pd.read_csv("code/01_data acquisition/dataset.csv")
einwohner = pd.read_csv('data/einwohner_bundeslaender.csv', sep='\t')
bland="Bayern"

# get subset
# Use morgenpost because it contains "recovered"
wantedcols = indata.columns.str.contains(bland+":morgenpost")#:RKI
indata = indata.loc[:,wantedcols]
#rename cols
indata.columns = indata.columns.str.strip(bland+":morgenpost:")
# use only from first infection on
indata = indata.loc[indata.confirmed>0,:]

# Initial values
N = einwohner.loc[einwohner.Bundesland==bland].Einwohner.values#n population
I0 = indata.confirmed.iloc[0]#case number on first day of infections
N0 = N-I0#susceptible on first day
beta0 = 2/10 # to be calibrated
gamma = 0.97/14  #recovery rate, fixed
delta = 0.03/14  #death rate, fixed
group_names = [bland]
timesteps=len(indata)


# derive needed cols + order indata
I = indata["confirmed"]-indata["covered"]-indata["death"]
I[I<0] = 0#sometimes there are more recovered than infected (?)
I = I.values
S = pd.Series(N).repeat(len(indata)).values - I - indata["covered"].values - indata["death"].values
E = indata["death"].values
R = indata["covered"].values
y = np.stack([S,E,I,R],axis=1)

################
###FIT
################
#TODO: Add R2-Calc
# # fit model to data
fit_pan = panfit.FitPandemicSimulator(beta=beta0, gamma=gamma, delta=delta, N=N, y=y,timesteps=timesteps,group_names=group_names)
#result = fit_pan.fit_SEIR()
#betaest = result.x[0]#[0] to drop np.array, otherwise __init__ does not turn it into vector
fit_pan.fit_and_show_results()
df = fit_pan.fit_and_extract_df()
# fit_pan.simulate_SEIR()
# fit_pan.simulate_and_show_results()
#

from importlib import reload
reload(panfit)
reload(pansingle)
#dummy_y.flatten()
