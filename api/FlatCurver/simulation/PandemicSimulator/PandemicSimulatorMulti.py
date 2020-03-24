import numpy as np
import matplotlib.pyplot as plt
from copy import copy
import pandas as pd


from .PandemicSimulator import PandemicSimulator


class PandemicSimulatorMulti(PandemicSimulator):

    def __init__(self, beta, gamma, delta, N, group_names, timesteps):
        # inheriting super init leads to problems, since y0 is set in PandemicSimulator and constructs the y0 as N-1 while N can be a list in here
        self.beta = self.make_time_dependent(beta, timesteps)
        self.gamma = self.make_time_dependent(gamma, timesteps)
        self.delta = self.make_time_dependent(delta, timesteps)
        self.N = N
        self.group_names = group_names
        self.timesteps = timesteps
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)
        self.y0 = None
        self.ndim = beta[0].shape[0]  # use first element of list to determine the dimensions of simulation

        self.assertions()

    @staticmethod
    def make_time_dependent(parameter, timesteps):
        if not isinstance(parameter, list):
            parameter = copy([parameter] * timesteps)
        return parameter

    def assertions(self):
        assert isinstance(self.N, np.ndarray)
        assert len(self.beta) == self.timesteps
        assert len(self.gamma) == self.timesteps
        assert len(self.delta) == self.timesteps
        assert self.beta[0].shape[0] == len(self.group_names)
        assert self.gamma[0].shape[0] == len(self.group_names)
        assert self.delta[0].shape[0] == len(self.group_names)

    def simulate_SEIR(self):
        # TODO: make this unnecessary. See todo in line 12
        assert self.y0 is not None, "set y0 before calling simulate_SEIR"
        return super().simulate_SEIR()

    def deriv(self, t, y):
        """function which is to be optimized with scipy.integrate.solve_ivp."""
        S, E, I, R = [y[self.ndim * i:self.ndim * (i + 1)] for i in range(4)]
        td = int(t)
        dSdt = -1 * np.dot(self.beta[td], I / self.N) * S
        dEdt = np.dot(self.delta[td], I)
        dRdt = np.dot(self.gamma[td], I)
        dIdt = 1 / self.N * np.dot(self.beta[td], I) * S - dEdt - dRdt
        return [*dSdt, *dEdt, *dIdt, *dRdt]

    def plot(self, sol):
        fig = plt.figure(facecolor='w', figsize=(20, 10))
        for i in range(self.ndim):
            ax = plt.subplot(self.ndim, 1, i + 1)
            ax.plot(sol.t, sol.y[i, :] / self.N[i], 'b', alpha=0.5, lw=2, label=f'Susceptible_{i}')
            ax.plot(sol.t, sol.y[self.ndim + i, :] / self.N[i], 'r', alpha=0.5, lw=2, label=f'Dead_{i}')
            ax.plot(sol.t, sol.y[2 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Infections_{i}')
            ax.plot(sol.t, sol.y[3 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Recovered_with_immunity_{i}')
            self.plotting_standards(ax)
