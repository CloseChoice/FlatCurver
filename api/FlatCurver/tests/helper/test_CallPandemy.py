import unittest

from FlatCurver.helper.CallPandemy import CallPandemy

class TestCallPandemy(unittest.TestCase):

    @classmethod
    def setUp(cls):
        cls.beta_dct = {'2020-01-27': 0.03, '2020-03-10':0.05}
        cls.timesteps = 200

    def test_call_simulation_germany(self):
        caller = CallPandemy()
        df = caller.call_simulation_germany(self.beta_dct)
        assert df
