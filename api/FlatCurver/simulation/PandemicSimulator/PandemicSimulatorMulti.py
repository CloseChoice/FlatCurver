import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp
from copy import copy


from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator


class PandemicSimulatorMulti(PandemicSimulator):

    def __init__(self, beta, gamma, delta, N, timesteps=400):
        # TODO: inherit this from PandemicSimulator. Therefore get rid of transform_beta or write it as class method.
        super().__init__(beta, gamma, delta, N, timesteps)
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

    def simulate_SEIR(self):
        # TODO: make this unnecessary. See todo in line 12
        # TODO: way too much code copied here from base class
        assert self.y0 is not None, "set y0 before calling simluate_SEIR"

        def deriv_multi(t, y):
            S, E, I, R = [y[self.ndim*i:self.ndim*(i+1)] for i in range(4)]
            td = int(t)
            dSdt = -1*np.dot(self.beta[td], I/self.N)*S
            dEdt = np.dot(self.delta[td], I)
            dRdt = np.dot(self.gamma[td], I)
            dIdt = 1/self.N*np.dot(self.beta[td], I)*S-dEdt-dRdt
            return [*dSdt, *dEdt, *dIdt, *dRdt]

        return solve_ivp(deriv_multi, (0, self.timesteps - 1), y0=self.y0, t_eval=np.linspace(0, self.timesteps-1,
                                                                                              self.timesteps))

    def plot(self, sol):
        fig = plt.figure(facecolor='w', figsize=(20, 10))
        for i in range(self.ndim):
            ax = plt.subplot(self.ndim, 1, i + 1)
            ax.plot(sol.t, sol.y[i, :] / self.N[i], 'b', alpha=0.5, lw=2, label=f'Susceptible_{i}')
            ax.plot(sol.t, sol.y[self.ndim + i, :] / self.N[i], 'r', alpha=0.5, lw=2, label=f'Dead_{i}')
            ax.plot(sol.t, sol.y[2 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Infections_{i}')
            ax.plot(sol.t, sol.y[3 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Recovered_with_immunity_{i}')
            self.plotting_standards(ax)
