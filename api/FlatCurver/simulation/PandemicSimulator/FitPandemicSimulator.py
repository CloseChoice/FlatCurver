import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator

class FitPandemicSimulator(PandemicSimulator):
    def __init__(self, beta, gamma, delta, N, y, group_names,timesteps=400):

        self.beta = self.make_time_dependent(beta, timesteps)
        self.gamma = self.make_time_dependent(gamma, timesteps)
        self.delta = self.make_time_dependent(delta, timesteps)
        self.N = N
        self.timesteps = timesteps
        self.y0 = [self.N - 1, 0, 1, 0]
        self.y = y
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)
        self.group_names = group_names

    def assertions(self):
        assert len(self.beta) == self.timesteps
        assert len(self.y) == self.timesteps
        assert not self.group_names or isinstance(self.group_names, list)

    def set_y0(self, y):
        self.y0 = y[0,:]

    def _residuals(self, estbeta):
        self.beta = self.make_time_dependent(estbeta[0], self.timesteps)#[0] so that it is automatically turned into vector
        output = self.simulate_extract_df().to_numpy()
        residuals = output.flatten() - self.y.flatten() #leastqsr sovler only accepts 1D-outputs
        return residuals

    def fit_SEIR(self):
        x_0 = 5#starting value
        #bounds = [0,5]
        result = least_squares(fun=self._residuals, x0=x_0, method='lm')  #bounds=bounds
        return(result)
