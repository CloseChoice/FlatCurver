import unittest
import numpy as np

from FlatCurver.simulation.PandemicSimulator.PandemicSimulatorMulti import PandemicSimulatorMulti


class TestPandemicSimulatorMulti(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.ger_pop = 8 * 10e7  # german population
        cls.ndim = 2
        cls.beta = np.array([[1, 3 / 10], [1 / 10, 2 / 10]])  # contact rate: given by RKI, a patient is 10 days infectious and infects 2 people during this time
        cls.gamma = np.diag([0.97 / 14, 0.96 / 14])  # recovery rate: 0.97 percent survive while the average infection lasts for 14 days
        cls.delta = np.diag([0.03 / 14, 0.04 / 14])  # death rate: 1-gamma
        cls.N = np.array([0.6 * cls.ger_pop, 0.4 * cls.ger_pop])

    def test_running(self):
        pan_obj = PandemicSimulatorMulti(beta=self.beta, gamma=self.gamma, delta=self.delta, N=self.N, timesteps=600)
        pan_obj.set_y0([self.N[0]-1, self.N[1], 1, 0, 0, 0, 0, 0])
        sol = pan_obj.simulate_SEIR()
        assert sol.y.shape == (8, 600)
