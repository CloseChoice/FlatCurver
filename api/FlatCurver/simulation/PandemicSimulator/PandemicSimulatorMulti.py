import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp


from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator


class PandemicSimulatorMulti(PandemicSimulator):

    def __init__(self, beta, gamma, delta, N, timesteps=400):
        # TODO: inherit this from PandemicSimulator. Therefore get rid of transform_beta or write it as class method.
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.N = N
        self.timesteps = timesteps
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)
        self.y0 = None
        self.ndim = beta.shape[0]

    @staticmethod
    def transform_beta(beta, timesteps):
        return beta

    def assertions(self):
        #TODO: check whether gamma and delta are diag matrices and if beta.shape ==
        assert isinstance(self.beta, np.array)
        assert isinstance(self.gamma, np.array)
        assert isinstance(self.delta, np.array)
        assert isinstance(self.N, np.array)
        assert self.beta.shape == self.gamma.shape == self.delta.shape

    def simulate_SEIR(self):
        # TODO: make this unnecessary. See todo in line 12
        # TODO: way to much code copied here from base class
        assert self.y0 is not None, "set y0 before calling simluate_SEIR"
        def deriv_multi(t, y):
            S, I, R, D = [y[self.ndim*i:self.ndim*(i+1)] for i in range(4)]
            dSdt = -1*np.dot(self.beta, I/self.N)*S
            dDdt = np.dot(self.delta, I)
            dRdt = np.dot(self.gamma, I)
            dIdt = 1/self.N*np.dot(self.beta, I)*S-dDdt-dRdt
            return [*dSdt, *dIdt, *dRdt, *dDdt]
        return solve_ivp(deriv_multi, (0, self.timesteps - 1), y0=self.y0, t_eval=np.linspace(0, self.timesteps-1,
                                                                                              self.timesteps))

    def plot(self, sol):
        fig = plt.figure(facecolor='w', figsize=(20, 10))
        for i in range(self.ndim):
            ax = plt.subplot(self.ndim, 1, i + 1)
            ax.plot(sol.t, sol.y[i, :] / self.N[i], 'b', alpha=0.5, lw=2, label=f'Susceptible_{i}')
            ax.plot(sol.t, sol.y[self.ndim + i, :] / self.N[i], 'r', alpha=0.5, lw=2, label=f'Infected_{i}')

            ax.plot(sol.t, sol.y[2 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Recovered with immunity_{i}')

            ax.plot(sol.t, sol.y[3 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Dead_{i}')
            self.plotting_standards(ax)
