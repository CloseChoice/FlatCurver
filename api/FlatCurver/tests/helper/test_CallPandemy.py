import unittest
import requests
from ...helper.CallPandemy import CallPandemy


class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.3, '2020-03-10': 0.4}
        cls.timesteps = 200
        cls.url = "http://flatcurverapi.eu.pythonanywhere.com"

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
