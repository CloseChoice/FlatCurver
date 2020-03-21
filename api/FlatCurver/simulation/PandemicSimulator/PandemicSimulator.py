import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


class PandemicSimulator:
    START_DATE = '2020-01-27'

    # TODO: this currently only supports the one-dim case. Can this be generalized to fit multi-dim purposes?
    # TODO: functionality to export data
    # TODO: add docstrings

    def __init__(self, beta, gamma, delta, N, timesteps=400):
        # TODO: make beta time dependent
        self.beta = self.transform_beta(beta, timesteps)
        self.gamma = gamma
        self.delta = delta
        self.N = N
        self.timesteps = timesteps
        self.y0 = [self.N - 1, 0, 1, 0]
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)

        self.assertions()

    @staticmethod
    def transform_beta(beta, timesteps):
        return [beta] * timesteps if type(beta) != np.array else beta

    def sinusoidal_decay(self, seasonality, length):
        R0 = 2
        if seasonality == 'weak':
            a = 0.6
        elif seasonality == 'strong':
            a = 1.33
        else:
            raise ValueError(f"seasonality {seasonality} not found")
        return -a * np.sin([2 * np.pi * i / (2 * length) for i in range(length)]) + R0

    def assertions(self):
        assert len(self.beta) == self.timesteps

    def set_y0(self, y0):
        self.y0 = y0

    def simulate_SEIR(self):
        def deriv_time_dep(t, y):
            S, E, I, R = y
            dSdt = -1 / self.N * self.beta[int(t)] * I * S
            dEdt = self.delta * I
            dRdt = self.gamma * I
            dIdt = 1 / self.N * self.beta[int(t)] * I * S - dEdt - dRdt
            return dSdt, dEdt, dIdt, dRdt
        sol = solve_ivp(deriv_time_dep, (0, self.timesteps - 1), y0=self.y0,
                        t_eval=np.linspace(0, self.timesteps - 1, self.timesteps))
        return sol

    def simulate_and_show_results(self):
        sol = self.simulate_SEIR()
        self.plot(sol)

    def plotting_standards(self, ax):
        ax.set_xlabel('Time /days')
        ax.set_ylabel('Number (percent of total population)')
        ax.set_ylim(0, 1.2)
        ax.yaxis.set_tick_params(length=0)
        ax.xaxis.set_tick_params(length=0)
        ax.grid(b=True, which='major', c='w', lw=2, ls='-')
        legend = ax.legend()
        legend.get_frame().set_alpha(0.5)
        for spine in ('top', 'right', 'bottom', 'left'):
            ax.spines[spine].set_visible(False)

    def plot(self, sol):
        fig = plt.figure(facecolor='w', figsize=(20, 10))
        ax = fig.add_subplot(111, axisbelow=True)
        ax.plot(self.dates[sol.t.astype(int)], sol.y[0, :] / self.N, 'b', alpha=0.5, lw=2, label=f'Susceptible')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[1, :] / self.N, 'r', alpha=0.5, lw=2, label=f'Dead')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[2, :] / self.N, 'g', alpha=0.5, lw=2, label=f'Infected')
        ax.plot(self.dates[sol.t.astype(int)], sol.y[3, :] / self.N, 'black', alpha=0.5, lw=2,
                label=f'Recovered with immunity')
        self.plotting_standards(ax)
