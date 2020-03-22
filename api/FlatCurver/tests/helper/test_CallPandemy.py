import unittest

from ...helper.CallPandemy import CallPandemy


class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.3, '2020-03-10': 0.4}
        cls.timesteps = 200

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        json = caller.call_simulation_germany(self.beta_dct)
        assert json
