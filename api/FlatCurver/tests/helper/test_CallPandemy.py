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
        cls.ordered_betas = OrderedDict({"Baden-Wuerttemberg":  {"2020-01-27":  1, "2020-02-25": 1.5}, "Bayern":  {"2020-01-27":  4, "2020-03-01": 1.7}}.items())

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        json = caller.call_simulation_germany(self.beta_dct)
        assert json

    def test_online_api(self):
        response = requests.post(self.url + '/simulate', json=self.beta_dct)
        assert response

    def test_online_api_debug(self):
        response = requests.get(self.url + '/debug', json=self.beta_dct)
        assert response

    def test_call_simulation_bundeslaender(self):
        caller = CallPandemy()
        path = os.path.dirname(os.path.abspath(__file__))
        data_json_path = os.path.join(path, 'data.json')
        json_ = json.load(open(data_json_path))
        caller.call_simulation_bundeslaender(beta_dct=json_, gamma={}, delta={}, timesteps=400)

    def test_create_matrices(self):
        caller = CallPandemy()
        num_timesteps = 3
        matrix = caller.create_matrices(self.ordered_betas, timesteps=num_timesteps)
        expected_matrix = [np.array([[1., 0.], [0., 4.]])] * num_timesteps
        for m1, m2 in zip(matrix, expected_matrix):
            np.testing.assert_array_equal(m1, m2)

