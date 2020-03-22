import unittest
import requests
from ...helper.CallPandemy import CallPandemy


class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.3, '2020-03-10': 0.4}
        cls.timesteps = 200
        cls.url = "http://euflatcurver.eu.pythonanywhere.com/welcome/api/simulate"
        cls.url_debug = "http://euflatcurver.eu.pythonanywhere.com/welcome/api/debug"

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        json = caller.call_simulation_germany(self.beta_dct)
        assert json

    def test_online_api(self):
        response = requests.post(self.url, json=self.beta_dct)
        print(f"status: {response.status_code}")
        print(f"text: {response.text}")
        print(f"json: {response.json()}")
        assert response

    def test_online_api_debug(self):
        response = requests.post(self.url_debug, json=self.beta_dct)
        print(f"status: {response.status_code}")
        print(f"text: {response.text}")
        print(f"json: {response.json()}")
        assert response
