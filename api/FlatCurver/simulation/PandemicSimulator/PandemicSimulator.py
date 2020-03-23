import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt


class PandemicSimulator:
    START_DATE = '2020-01-27'
    CONDITIONS = ['Susceptible', 'Dead', 'Infectious', 'Recovered']  #take care this is ordered
    # TODO: this currently only supports the one-dim case. Can this be generalized to fit multi-dim purposes?
    # TODO: functionality to export data
    # TODO: add docstrings

    def __init__(self, beta, gamma, delta, N, group_names, timesteps):
        self.beta = self.make_time_dependent(beta, timesteps)
        self.gamma = self.make_time_dependent(gamma, timesteps)
        self.delta = self.make_time_dependent(delta, timesteps)
        self.N = N
        self.group_names = group_names
        self.timesteps = timesteps
        self.y0 = [self.N - 1, 0, 1, 0]
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)

        self.assertions()

    @staticmethod
    def make_time_dependent(parameter, timesteps):
        return [parameter] * timesteps if not isinstance(parameter, (np.ndarray, list)) else parameter

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
        assert not self.group_names or isinstance(self.group_names, list)

    def set_y0(self, y0):
        self.y0 = y0

    def simulate_SEIR(self):
        sol = solve_ivp(self.deriv, (0, self.timesteps - 1), y0=self.y0,
                        t_eval=np.linspace(0, self.timesteps - 1, self.timesteps))
        return sol

    def deriv(self, t, y):
        S, E, I, R = y
        td = int(t)
        dSdt = -1 / self.N * self.beta[td] * I * S
        dEdt = self.delta[td] * I
        dRdt = self.gamma[td] * I
        dIdt = 1 / self.N * self.beta[td] * I * S - dEdt - dRdt
        return dSdt, dEdt, dIdt, dRdt

    def simulate_and_show_results(self):
        sol = self.simulate_SEIR()
        self.plot(sol)

    def plotting_standards(self, ax):
        ax.set_xlabel('Time /days')
        ax.set_ylabel('Number (percent of total population)')
        #ax.set_ylim(0.9, 1.1)#CHANGED
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

    def simulate_extract_df(self):
        """simulate and return dataframe"""
        sol = self.simulate_SEIR()
        col_names = [f'{cond}_{group}' for cond in self.CONDITIONS for group in self.group_names]
        print(col_names)
        df = pd.DataFrame(sol.y.T, index=self.dates[sol.t.astype(int)], columns=col_names)
        return df

    def simulate_and_export(self):
        """simulate and export to json"""
        df = self.simulate_extract_df()
        return df.to_json(orient='records')
