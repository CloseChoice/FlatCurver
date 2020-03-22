import unittest
from collections import OrderedDict
import numpy as np

from ...helper.CallPandemy import CallPandemy


class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.3, '2020-03-10': 0.4}
        cls.timesteps = 200
        cls.ordered_betas = OrderedDict({"Baden-Württemberg":  {"2020-01-27":  1, "2020-02-25": 1.5}, "Bayern":  {"2020-01-27":  4, "2020-03-01": 1.7}}.items())

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        json = caller.call_simulation_germany(self.beta_dct)
        assert json

    def test_call_simulation_bundeslaender(self):
        caller = CallPandemy()
        caller.call_simulation_bundeslaender(beta_dct=None, gamma=None, delta=None, timesteps=50)

    def test_create_matrices(self):
        caller = CallPandemy()
        matrix = caller.create_matrices(self.ordered_betas, timesteps=3)
        expected_matrix = [np.array([[1, 0], [4, 0]]), np.array([[1, 0], [4, 0]]), np.array([[1, 0], [4, 0]])]

