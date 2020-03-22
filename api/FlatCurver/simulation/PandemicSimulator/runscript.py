import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
#os.getcwd()
#os.chdir("/Users/schmidle/Documents/GIT-Projects/FlatCurver/api")
#os.chdir("/Users/schmidle/Documents/GIT-Projects/FlatCurver/api/FlatCurver/simulation/PandemicSimulator")

module_folder = os.path.abspath('/Users/schmidle/Documents/GIT-Projects/FlatCurver/api')
#module_folder = 'src/'
if module_folder not in sys.path:
    sys.path.append(module_folder)

sys.path
import FlatCurver.simulation.PandemicSimulator.PandemicSimulatorMulti as pan
import FlatCurver.simulation.PandemicSimulator.FitPandemicSimulator as panfit


### Normal Multi
ger_pop = 8*10e7  #german population
ndim = 2
beta = np.array([[1, 3/10], [1/10, 2/10]])  # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
gamma = np.diag([0.97/14, 0.96/14])  #recovery rate: 0.97 percent survive while the average infection lasts for 14 days
delta = np.diag([0.03/14, 0.04/14])  #death rate: 1-gamma
N = np.array([0.6*ger_pop, 0.4 * ger_pop])
# %% codecell
multi_pan = pan.PandemicSimulatorMulti(beta=beta, gamma=gamma, delta=delta, N=N, timesteps=600)
# %% codecell
multi_pan.set_y0([N[0]-1, N[1], 1, 0, 0,0, 0,0])
# %% codecell
sol = multi_pan.simulate_SEIR()
# %% codecell
multi_pan.simulate_and_show_results()




### MyCalibration (only single input model)
beta = 2/10  # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
gamma1 = 0.97/14  #recovery rate: 0.97 percent survive while the average infection lasts for 14 days
delta1 = 0.03/14  #death rate: 1-gamma
N = 8*10e7  #german population
timesteps=600

dummy_y = np.array([[N - 1, 0, 1, 0],]*timesteps)

fit_pan = panfit.FitPandemicSimulator(beta=beta, gamma=gamma, delta=delta, N=N, y=dummy_y,timesteps=timesteps)
fit_pan.fit_SEIR()

#Hakunama
f
