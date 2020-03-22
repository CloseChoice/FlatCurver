import pandas as pd
import numpy as np

from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator
from FlatCurver.simulation.PandemicSimulator.PandemicSimulatorMulti import PandemicSimulatorMulti
from FlatCurver.helper import utils


class CallPandemy:
    BETA_NEIGHBORS_OFFDIAG = 0.01
    BETA_NEIGHBORS = 0.05
    GAMMA_NEIGHBORING = 0.01
    DELTA_NEIGHBORING = 0.001
    NEIGHBORS_INHABITANTS = 15e7
    DEFAULT_GAMMA_DCT = {'2020-01-27': 0.97/14}
    DEFAULT_DELTA_DCT = {'2020-01-27': 0.03/14}
    DEFAULT_TIMESTEPS = 200

    PATH_TO_CSV = '/home/tobias/programming/python/corona_simulation/FlatCurver/data/einwohner_bundeslaender.csv'
    def __init__(self):
        # TODO: exchange path
        pop_df = pd.read_csv(self.PATH_TO_CSV, sep='\t')
        self.pop_bundeslaender = pop_df.set_index('Bundesland').to_dict()['Einwohner']
        self.population_germany = sum(self.pop_bundeslaender.values())

    def construct_time_dependent_beta(self, beta_dct, timesteps):
        return utils.arrange_dates(beta_dct, timesteps=timesteps)

    def call_simulation_bundeslaender(self):
        # TODO: decide wheether neighboring countries shall be taken into account
        pass

    def calculate_values_neighbors(self, beta, gamma, delta, N):
        """helper function to create the beta, gamma and delta matrices. This takes a scalar beta, gamma and delta
        and returns matrices where the added information shall correspond to the impact of all neighboring countries
        on Germany"""

        beta_lst = []
        for beta_t in beta:
            beta_lst.append(np.array([[beta_t, self.BETA_NEIGHBORS_OFFDIAG], [self.BETA_NEIGHBORS_OFFDIAG,
                                                                              self.BETA_NEIGHBORS]]))
        gamma_lst = []
        for gamma_t in gamma:
            gamma_lst.append(np.diag([gamma_t, self.GAMMA_NEIGHBORING]))
        delta_lst = []
        for delta_t in delta:
            delta_lst.append(np.diag([delta_t, self.DELTA_NEIGHBORING]))
        N_lst = np.array([N, self.NEIGHBORS_INHABITANTS])
        return beta_lst, gamma_lst, delta_lst, N_lst

    def call_simulation_germany(self, beta_dct, gamma=None, delta=None, timesteps=None):
        gamma = gamma or self.DEFAULT_GAMMA_DCT
        delta = delta or self.DEFAULT_DELTA_DCT
        timesteps = timesteps or self.DEFAULT_TIMESTEPS
        beta_lst = self.construct_time_dependent_beta(beta_dct, timesteps=timesteps)
        gamma_lst = self.construct_time_dependent_beta(gamma, timesteps=timesteps)
        delta_lst = self.construct_time_dependent_beta(delta, timesteps=timesteps)
        beta_ng, gamma_ng, delta_ng, N_ng = self.calculate_values_neighbors(beta_lst, gamma_lst, delta_lst,
                                                                            self.population_germany)
        import pdb; pdb.set_trace()
        pandemic_caller = PandemicSimulatorMulti(beta=beta_ng, gamma=gamma_ng, delta=delta_ng, N=N_ng,
                                                 group_names=['Germany', 'Neigbhors'])
        pandemic_caller.set_y0([N_ng[0]-1, N_ng[1]-1000, 0, 0, 0, 1, 1000, 0, 0])
        return pandemic_caller.simulate_extract_df()



