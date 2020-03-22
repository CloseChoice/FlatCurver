import unittest
import requests
from collections import OrderedDict
import numpy as np
import json
import os

from FlatCurver.helper.CallPandemy import CallPandemy



class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.3, '2020-03-10': 0.4}
        cls.timesteps = 200
        cls.url = "http://flatcurverapi.eu.pythonanywhere.com"
        cls.ordered_betas = OrderedDict({"Baden-Wuerttemberg":  {"2020-01-27":  1, "2020-02-25": 1.5}, "Bayern":  {"2020-01-27":  4, "2020-03-01": 1.7}})
        path = os.path.dirname(os.path.abspath(__file__))
        data_json_path = os.path.join(path, 'data.json')
        cls.all_betas = json.load(open(data_json_path, 'r'))
        cls.jsondata = json.load(open(os.path.join(path, 'data_flask.json'), 'r'))

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        result = caller.call_simulation_germany(self.beta_dct, gamma={}, delta={}, timesteps=200)
        assert result

    def test_online_api(self):
        response = requests.post(self.url + '/simulate', json=self.jsondata)
        assert response

    def test_online_api_debug(self):
        response = requests.get(self.url + '/debug', json=self.beta_dct)
        assert response

    def test_call_simulation_bundeslaender(self):
        caller = CallPandemy()
        caller.call_simulation_bundeslaender(self.all_betas, gamma={}, delta={}, timesteps=400)

    def test_create_matrices(self):
        caller = CallPandemy()
        num_timesteps = 3
        matrix = caller.create_matrices(self.ordered_betas, timesteps=num_timesteps)
        expected_matrix = [np.array([[1., 0.], [0., 4.]])] * num_timesteps
        for m1, m2 in zip(matrix, expected_matrix):
            np.testing.assert_array_equal(m1, m2)

    def test_flask_stuff(self):
        # TODO: improve this test. Check how flask is usually tested and use this
        from FlatCurver.helper.CallPandemy import CallPandemy
        SIMULATED_TIMESTEPS = 200
        json_ger = self.jsondata.pop('Deutschland')
        caller = CallPandemy()
        result_bl = caller.call_simulation_bundeslaender(self.jsondata, gamma={}, delta={}, timesteps=SIMULATED_TIMESTEPS)
        result_ger = caller.call_simulation_germany(json_ger, gamma={}, delta={}, timesteps=SIMULATED_TIMESTEPS)
        result_bl.update(result_ger)


