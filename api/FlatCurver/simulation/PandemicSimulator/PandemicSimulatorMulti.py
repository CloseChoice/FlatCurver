import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp


from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator

def vhelp(x):
    # used to help with delta to gamma
    # gamma is always 1-delta, except if gamma is 0 then we usually have an error (lol)
    y = round(1-x,2)
    if y >= 0.999:
        return 0
    else:
        return y

vfunc = np.vectorize(lambda x: vhelp(x))


class PandemicSimulatorMulti(PandemicSimulator):

    def __init__(self, beta, gamma, delta, N, timesteps=400,names=None,hospital_rates=None,lethality_factor=1):
        # TODO: inherit this from PandemicSimulator. Therefore get rid of transform_beta or write it as class method.
        self.beta = beta
        # beta is a matrix of the form 16x16
        # where every country has one infection rate for every other country 
        # this is used to simulate e.g. how bavarians can infect berlin ppl if only one side closes the borders


        self.gamma = gamma
        self.delta = delta
        # Gamma and delta also are 16x16 but only have one value in the diagonal 
        # They have to be that way for easy matrix multiplication 
        # We could do some strange math to do it, but its easier to just make the matrixes

        self.N = N
        # N is a vector

        self.timesteps = timesteps
        self.dates = pd.date_range(start=self.START_DATE, periods=timesteps)
        self.y0 = None
        # y0 is a vector which holds a quadruple of (remainingPop,currentInfected,currentRecovered,currentDeath)

        self.names=names 
        # Store the names of each dimensions
        # These could be for example bundeslaender or age-groups
        self.ndim = beta.shape[0]

        self.hospital_rates = hospital_rates 
        # A percentage how many people of the population can be infected at once without applying the additional lethality factor
        # Hospital_rates are also a n-dimensional vector
        self.lethality_factor = lethality_factor
        # A coefficient to the lethality if the hospital_rates are exceeded

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
        if self.names:
            assert self.ndim == len(self.names), "number of names must match the dimensions"

    def simulate_SEIR(self):
        '''
        S = Suspectable 
        I = Infected
        R = Recovered
        D = Dead
        dXdt = derivative of X over time

        The values are being flattened together into one list with *dSdt and the resulting list can be used for solve_ivp
        '''
        assert self.y0 is not None, "set y0 before calling simulate_SEIR"
        def deriv_multi(t, y):
            S, I, R, D = [y[self.ndim*i:self.ndim*(i+1)] for i in range(4)]
            dSdt = -1*np.dot(self.beta, I/self.N)*S
            
            # To apply the correct number of deaths and recoveries, we make a temporary copy 
            # We change values where fit and calculate current deaths and recoveries 
            # for further use in the function we pass the normal deltas
            temp_delta = self.delta.copy()

            if self.hospital_rates and self.lethality_factor:
                for i in range(len(I)):
                    if I[i]>self.hospital_rates[i]:
                        temp_delta[i][i] = self.delta[i][i]*self.lethality_factor
            temp_gamma = vfunc(temp_delta)

            dDdt = np.dot(temp_delta, I)
            dRdt = np.dot(temp_gamma, I)

            dIdt = 1/self.N*np.dot(self.beta, I)*S-dDdt-dRdt
            return [*dSdt, *dIdt, *dRdt, *dDdt]
        return solve_ivp(deriv_multi, 
                        (0, self.timesteps - 1), 
                        y0=self.y0, 
                        t_eval=np.linspace(0, self.timesteps-1,self.timesteps))

    def plot(self, sol):
        for i in range(self.ndim):
            fig = plt.figure(facecolor='w', figsize=(20, 10))
            ax = plt.subplot(1,1,1)
            if self.names:
                ax.plot(sol.t, sol.y[i, :] / self.N[i], 'b', alpha=0.5, lw=2, label=f'Susceptible_{self.names[i]}')
                ax.plot(sol.t, sol.y[self.ndim + i, :] / self.N[i], 'r', alpha=0.5, lw=2, label=f'Infected_{self.names[i]}')
                ax.plot(sol.t, sol.y[2 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Recovered with immunity_{self.names[i]}')
                ax.plot(sol.t, sol.y[3 * self.ndim + i, :] / self.N[i], 'black', alpha=0.5, lw=2, label=f'Dead_{self.names[i]}')
                self.plotting_standards(ax,self.names[i])
            else:
                ax.plot(sol.t, sol.y[i, :] / self.N[i], 'b', alpha=0.5, lw=2, label=f'Susceptible_{i}')
                ax.plot(sol.t, sol.y[self.ndim + i, :] / self.N[i], 'r', alpha=0.5, lw=2, label=f'Infected_{i}')
                ax.plot(sol.t, sol.y[2 * self.ndim + i, :] / self.N[i], 'g', alpha=0.5, lw=2, label=f'Recovered with immunity_{i}')
                ax.plot(sol.t, sol.y[3 * self.ndim + i, :] / self.N[i], 'black', alpha=0.5, lw=2, label=f'Dead_{i}')
                self.plotting_standards(ax)
            plt.show()