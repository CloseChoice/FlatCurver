import unittest
import numpy as np

from FlatCurver.simulation.PandemicSimulator.PandemicSimulator import PandemicSimulator


class TestPandemicSimulator(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.beta = 2 / 10  # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
        cls.gamma = 0.97 / 9  # recovery rate: 0.97 percent survive while the average infection lasts for 14 days
        cls.delta = 0.03 / 14  # death rate: 1-gamma
        cls.N = 8 * 10e7  # german population
        cls.ger_pop = 8 * 10e7  # german population

    def test_running(self):
        pan_obj = PandemicSimulator(beta=self.beta, gamma=self.gamma, delta=self.delta, N=self.N,
                                    group_names=['Deutschland'], timesteps=600)
        sol = pan_obj.simulate_SEIR()
        assert sol.y.shape == (4, 600)
