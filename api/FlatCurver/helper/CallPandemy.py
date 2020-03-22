import pandas as pd
import numpy as np
import os
import json
from collections import OrderedDict
from copy import copy
import matplotlib
from matplotlib import cm
import re

from ..simulation.PandemicSimulator.PandemicSimulatorMulti import PandemicSimulatorMulti
from .utils import arrange_dates, update


class CallPandemy:
    BETA_NEIGHBORS_OFFDIAG = 0.01
    BETA_NEIGHBORS = 0.05
    GAMMA_NEIGHBORING = 0.01
    DELTA_NEIGHBORING = 0.001
    NEIGHBORS_INHABITANTS = 15e7
    DEFAULT_GAMMA_DCT = {'2020-01-27': 0.97/14}
    DEFAULT_DELTA_DCT = {'2020-01-27': 0.03/14}
    DEFAULT_TIMESTEPS = 200
    
    _package_directory = os.path.dirname(os.path.abspath(__file__))
    PATH_TO_CSV = os.path.join(_package_directory, '../../../data/einwohner_bundeslaender.csv')
    PATH_TO_DEFAULT_JSON = os.path.join(_package_directory, 'default_params.json')
    def __init__(self):
        pop_df = pd.read_csv(self.PATH_TO_CSV, sep='\t')
        self.pop_bundeslaender = OrderedDict(sorted(pop_df.set_index('Bundesland').to_dict()['Einwohner'].items()))
        self.population_germany = sum(self.pop_bundeslaender.values())

    def construct_time_dependent_beta(self, beta_dct, timesteps):
        return arrange_dates(beta_dct, timesteps=timesteps)



    def call_simulation_bundeslaender(self, beta_dct, gamma, delta, timesteps):
        with open(self.PATH_TO_DEFAULT_JSON, 'r') as f:
            default_params = json.load(f)
            ordered_params = OrderedDict(sorted(default_params.items()))
        updated_params = self.update_params(ordered_params, beta_dct, gamma, delta)
        betas = self.create_matrices(updated_params['beta'], timesteps)
        gammas = self.create_matrices(updated_params['gamma'], timesteps)
        deltas = self.create_matrices(updated_params['delta'], timesteps)
        N = np.array(list(self.pop_bundeslaender.values()))

        pandemic_caller = PandemicSimulatorMulti(beta=betas, gamma=gammas, delta=deltas, N=N, group_names=list(self.pop_bundeslaender.keys()), timesteps=timesteps)
        pandemic_caller.set_y0([*N, *list([0]*16), *list([1]*16), *list([0]*16)])
        df = pandemic_caller.simulate_extract_df()
        df = self.adjust_dataframe_for_export(df)
        df = self.aggregate_bundeslaender_result(df)
        result_dct = self.get_correct_json_bundeslaender(df)
        return json.dump(result_dct, open('simulate_bundeslaender.json', 'w'), ensure_ascii=False)

    @staticmethod
    def aggregate_bundeslaender_result(df):
        df_agg = copy(df)
        for status in ['Susceptible', 'Dead', 'Infectious', 'Recovered']:
            df_agg[f'{status}_Deutschland'] = df[[col for col in df.columns if status in col]].sum(1)
        return df_agg


    def get_correct_json_bundeslaender(self, df):
        result_dct = {}
        norm = matplotlib.colors.Normalize(vmin=0.6, vmax=1, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm.RdYlGn)
        for bundesland in list(self.pop_bundeslaender.keys()) + ['Deutschland']:
            cols_bundesland = [col for col in df.columns if bundesland in col]
            df_bl = df[cols_bundesland + ['Timestamp']]
            new_colnames = [re.sub(f'_{bundesland}$', '', col) for col in df_bl.columns]
            df_bl.columns = new_colnames
            df_bl['InfectedRatio'] = df_bl['Infectious']/df_bl.sum(1)  # inefficient but should work, problem is that Deutschland is not in population csv
            df_bl['Color'] = df_bl['InfectedRatio'].apply(lambda x: matplotlib.colors.to_hex(mapper.to_rgba(1-x), keep_alpha=False).upper())
            result_dct[bundesland] = df_bl.to_dict(orient='list')
        return result_dct

    def convert_to_hex(self, df):
        df['Color'] = df['InfectedRatio']
        norm = matplotlib.colors.Normalize(vmin=0, vmax=0.4, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm.RdYlGn)

        for v in [0.2, 0.4]:
            print(matplotlib.colors.to_hex(mapper.to_rgba(v), keep_alpha=False).upper())


    def update_params(self, ordered_params, beta, gamma, delta):
        #TODO: update logic für Jsons schreiben: bspw. {'2020-01-01': 1, '2020-02-01': 4} und das update so aussieht {'2020-01-15':2} dann nur sachen nach dem 2020-01-15 überschreiben
        ordered_params['beta'] = update(ordered_params['beta'], beta)
        ordered_params['gamma'] = update(ordered_params['gamma'], gamma)
        ordered_params['delta'] = update(ordered_params['delta'], delta)
        return ordered_params

    @staticmethod
    def create_matrices(ordered_param, timesteps):
        params = pd.DataFrame({k: arrange_dates(v, timesteps) for k, v in ordered_param.items()})
        arr = []
        for ind, val in params.iterrows():
            arr.append(np.diag(val))
        return arr




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
        pandemic_caller = PandemicSimulatorMulti(beta=beta_ng, gamma=gamma_ng, delta=delta_ng, N=N_ng,
                                                 group_names=['Germany', 'Neighbors'], timesteps=timesteps)
        pandemic_caller.set_y0([N_ng[0]-1, N_ng[1]-1000, 0, 0, 1, 1000, 0, 0])

        df = pandemic_caller.simulate_extract_df()
        df = df[[col for col in df.columns if 'Germany' in col]]
        adjusted_df = self.adjust_dataframe_for_export(df)
        return self.dump_to_json(adjusted_df)

    def dump_to_json(self, df):
        dct = df.to_dict(orient='list')
        return json.dumps(dct)

    def adjust_dataframe_for_export(self, df):
        df = df.reset_index().rename(columns={'index': 'Timestamp'})
        df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d')
        return df

