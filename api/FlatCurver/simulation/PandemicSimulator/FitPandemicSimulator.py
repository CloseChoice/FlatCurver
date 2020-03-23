import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator

####TODO
# change y to yt becasue there already is y in deriv
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

    def _residuals(self, beta0):
        self.beta = self.make_time_dependent(beta0[0], self.timesteps)#[0] so that it is automatically turned into vector
        output = self.simulate_extract_df().to_numpy()
        residuals = output.flatten() - self.y.flatten() #leastqsr sovler only accepts 1D-outputs
        return residuals

    def fit_SEIR(self):
        x_0 = 5#starting value
        #bounds = [0,5]
        result = least_squares(fun=self._residuals, x0=x_0, method='lm')  #bounds=bounds
        beta_est = result.x[0]
        self.beta = self.make_time_dependent(beta_est, self.timesteps)#[0] so that it is automatically turned into vector
        print("Estimated beta: "+str(beta_est))
        return(beta_est)#estimated beta

    def fit_and_show_results(self):
        beta_est = self.fit_SEIR()
        sol = self.simulate_SEIR()
        self.plot(sol)

    def fit_and_extract_df(self):
        beta_est = self.fit_SEIR()
        df = self.simulate_extract_df()
        return(df)

    def plot(self, sol):
        # TODO
        # CALCULATE BACK INTO PERCENT  (/ self.N)
        fig = plt.figure(facecolor='w', figsize=(20, 10))
        ax = fig.add_subplot(111, axisbelow=True)
        # ax.plot(self.dates[sol.t.astype(int)], sol.y[0, :], 'b', alpha=0.5, lw=2, label=f'Susceptible')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[1, :], 'r', alpha=0.5, lw=2, label=f'Dead')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[2, :], 'g', alpha=0.5, lw=2, label=f'Infected')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[3, :], 'darkgrey', alpha=0.5, lw=2,
                label=f'Recovered with immunity')
        #ax.plot(self.dates[sol.t.astype(int)], self.y[:, 0], 'darkblue', alpha=0.5, lw=2, label=f'Susceptible')
        ax.plot(self.dates[sol.t.astype(int)], self.y[:, 1], 'darkred', alpha=0.5, lw=2, label=f'Dead')
        ax.plot(self.dates[sol.t.astype(int)], self.y[:, 2], 'darkgreen', alpha=0.5, lw=2, label=f'Infected')
        ax.plot(self.dates[sol.t.astype(int)], self.y[:, 3], 'black', alpha=0.5, lw=2,
                label=f'Recovered with immunity')
        self.plotting_standards(ax)
